#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de la aplicación
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Prueba que todas las dependencias se importen correctamente"""
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from dotenv import load_dotenv
        print("✅ Todas las dependencias se importan correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        return False

def test_app_creation():
    """Prueba que la aplicación se cree correctamente"""
    try:
        from app import app, db
        print("✅ La aplicación Flask se crea correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando la aplicación: {e}")
        return False

def test_database():
    """Prueba que la base de datos se configure correctamente"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ La base de datos se configura correctamente")
        return True
    except Exception as e:
        print(f"❌ Error configurando la base de datos: {e}")
        return False

def test_health_endpoint():
    """Prueba que el endpoint de health funcione"""
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ El endpoint /health funciona correctamente")
                return True
            else:
                print(f"❌ El endpoint /health devuelve código {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error probando el endpoint /health: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🔍 Iniciando pruebas de configuración...")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    tests = [
        test_imports,
        test_app_creation,
        test_database,
        test_health_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La aplicación está lista para desplegar.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 