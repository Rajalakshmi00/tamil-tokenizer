# Save this as "check_poppler.py" and run it to diagnose the issue

import os
import platform
from pdf2image import convert_from_path

def check_poppler_installation():
    """Diagnostic script to check poppler installation"""
    
    print("🔍 POPPLER DIAGNOSTIC CHECK")
    print("="*30)
    
    # Check 1: Operating System
    print(f"💻 Operating System: {platform.system()}")
    
    # Check 2: Expected poppler paths
    possible_paths = [
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin", 
        r"C:\Program Files\poppler\bin",
        r"C:\poppler-windows\Library\bin",
        r"C:\poppler-25.07.0\Library\bin"
    ]
    
    print("\n📁 Checking possible poppler paths:")
    found_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
            # Check if pdftoppm.exe exists
            pdftoppm_path = os.path.join(path, "pdftoppm.exe")
            if os.path.exists(pdftoppm_path):
                print(f"✅ pdftoppm.exe found: {pdftoppm_path}")
                found_path = path
            else:
                print(f"❌ pdftoppm.exe NOT found in: {path}")
        else:
            print(f"❌ Not found: {path}")
    
    # Check 3: PATH environment variable
    print("\n🛣️  Checking PATH environment variable:")
    path_env = os.environ.get('PATH', '')
    poppler_in_path = any('poppler' in p.lower() for p in path_env.split(';'))
    print(f"Poppler in PATH: {'✅ Yes' if poppler_in_path else '❌ No'}")
    
    # Check 4: Manual poppler test
    if found_path:
        print(f"\n🧪 Testing poppler with manual path: {found_path}")
        try:
            # Try to convert first page of a PDF (you need to have a PDF in same folder)
            pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
            if pdf_files:
                test_pdf = pdf_files[0]
                print(f"📄 Testing with PDF: {test_pdf}")
                
                # Try conversion with manual poppler path
                pages = convert_from_path(
                    test_pdf,
                    dpi=150,  # Lower DPI for faster test
                    first_page=1,
                    last_page=1,
                    poppler_path=found_path
                )
                
                if pages:
                    print("✅ SUCCESS! Poppler is working with manual path")
                    print(f"🎯 Use this path in your code: {found_path}")
                    return found_path
                else:
                    print("❌ Conversion returned no pages")
                    
            else:
                print("❌ No PDF files found for testing")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    # Check 5: List C:\ directory contents
    print("\n📂 Contents of C:\ drive:")
    try:
        c_contents = os.listdir("C:\\")
        poppler_folders = [item for item in c_contents if 'poppler' in item.lower()]
        if poppler_folders:
            print("Found poppler-related folders:")
            for folder in poppler_folders:
                print(f"  📁 C:\\{folder}")
                # Check contents of poppler folder
                folder_path = f"C:\\{folder}"
                if os.path.isdir(folder_path):
                    try:
                        contents = os.listdir(folder_path)
                        print(f"    Contents: {contents[:5]}")  # Show first 5 items
                    except:
                        print("    (Cannot read contents)")
        else:
            print("❌ No poppler folders found in C:\\")
    except Exception as e:
        print(f"❌ Cannot read C:\\ directory: {e}")
    
    return None

def show_fix_instructions():
    """Show instructions to fix poppler"""
    print("\n" + "="*50)
    print("🔧 HOW TO FIX POPPLER INSTALLATION")
    print("="*50)
    
    print("\nOPTION 1: Re-download and extract properly")
    print("-" * 45)
    print("1. Go to: https://github.com/oschwartz10612/poppler-windows/releases/")
    print("2. Download: poppler-xx.xx.x-x64.7z")
    print("3. Extract to C:\\ (not C:\\Users or Downloads)")
    print("4. Make sure you have: C:\\poppler\\Library\\bin\\pdftoppm.exe")
    
    print("\nOPTION 2: Try different extraction location")
    print("-" * 42)
    print("Extract to one of these locations:")
    print("- C:\\poppler\\")
    print("- C:\\poppler-windows\\")
    print("- C:\\Program Files\\poppler\\")
    
    print("\nOPTION 3: Add to Windows PATH")
    print("-" * 32)
    print("1. Copy the path where pdftoppm.exe is located")
    print("2. Press Win+R, type 'sysdm.cpl', press Enter")
    print("3. Click 'Environment Variables'")
    print("4. In System Variables, find 'Path' and click Edit")
    print("5. Click 'New' and paste your poppler bin path")
    print("6. Click OK on all windows")
    print("7. Restart your terminal/VSCode")

if __name__ == "__main__":
    working_path = check_poppler_installation()
    
    if not working_path:
        show_fix_instructions()
    else:
        print(f"\n🎉 Poppler is working! Use this path: {working_path}")
