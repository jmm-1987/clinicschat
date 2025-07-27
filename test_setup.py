#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración del proyecto
"""

import os
import sys

def test_imports():
    """Probar que todas las dependencias están instaladas"""
    try:
        import flask
        print("✅ Flask instalado correctamente")
    except ImportError:
        print("❌ Flask no está instalado")
        return False
    
    try:
        import openai
        print("✅ OpenAI instalado correctamente")
    except ImportError:
        print("❌ OpenAI no está instalado")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv instalado correctamente")
    except ImportError:
        print("❌ python-dotenv no está instalado")
        return False
    
    return True

def test_env_variables():
    """Probar que las variables de entorno están configuradas"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'tu_api_key_de_openai_aqui':
        print("✅ Variable OPENAI_API_KEY configurada")
        return True
    else:
        print("❌ Variable OPENAI_API_KEY no configurada o usando valor por defecto")
        print("   Por favor, configura tu API key en el archivo .env")
        return False

def test_files():
    """Probar que todos los archivos necesarios existen"""
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} no existe")
            all_exist = False
    
    return all_exist

def main():
    """Función principal"""
    print("🔍 Verificando configuración del proyecto...\n")
    
    # Probar archivos
    print("📁 Verificando archivos:")
    files_ok = test_files()
    print()
    
    # Probar imports
    print("📦 Verificando dependencias:")
    imports_ok = test_imports()
    print()
    
    # Probar variables de entorno
    print("🔐 Verificando variables de entorno:")
    env_ok = test_env_variables()
    print()
    
    # Resumen
    print("📊 Resumen:")
    if files_ok and imports_ok and env_ok:
        print("✅ Todo está configurado correctamente!")
        print("🚀 Puedes ejecutar 'python app.py' para iniciar el servidor")
    else:
        print("❌ Hay problemas en la configuración")
        if not files_ok:
            print("   - Faltan archivos del proyecto")
        if not imports_ok:
            print("   - Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        if not env_ok:
            print("   - Configura tu API key de OpenAI en el archivo .env")

if __name__ == "__main__":
    main() 