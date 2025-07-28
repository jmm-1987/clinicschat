#!/usr/bin/env python3
"""
Script de configuración y pruebas para el chatbot de clínica dental
"""

import os
import sys
import sqlite3
from datetime import datetime

def test_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.7+")
        return False

def test_dependencies():
    """Verifica las dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('python_dotenv', 'python-dotenv'),
        ('werkzeug', 'Werkzeug')
    ]
    
    all_installed = True
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} instalado correctamente")
        except ImportError:
            print(f"❌ {name} no está instalado")
            all_installed = False
    
    return all_installed

def test_environment():
    """Verifica las variables de entorno"""
    print("\n🔧 Verificando configuración del entorno...")
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
    else:
        print("⚠️  Archivo .env no encontrado (opcional)")
    
    # Verificar SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
    if secret_key and secret_key != 'tu-clave-secreta-aqui':
        print("✅ Variable SECRET_KEY configurada")
    else:
        print("⚠️  Variable SECRET_KEY no configurada o usando valor por defecto")
    
    return True

def test_database():
    """Verifica la base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        # Crear conexión a la base de datos
        conn = sqlite3.connect('instance/citas.db')
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cita'")
        if cursor.fetchone():
            print("✅ Tabla 'cita' existe en la base de datos")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM cita")
            count = cursor.fetchone()[0]
            print(f"📊 {count} citas registradas en la base de datos")
        else:
            print("⚠️  Tabla 'cita' no existe (se creará al ejecutar la aplicación)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False

def test_flask_app():
    """Verifica que la aplicación Flask se puede importar"""
    print("\n🚀 Verificando aplicación Flask...")
    
    try:
        # Cambiar al directorio del proyecto
        original_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Importar la aplicación
        from app import app, db
        
        # Crear contexto de aplicación
        with app.app_context():
            # Verificar que la base de datos se puede crear
            db.create_all()
            print("✅ Aplicación Flask importada correctamente")
            print("✅ Base de datos inicializada correctamente")
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"❌ Error al importar la aplicación Flask: {e}")
        os.chdir(original_dir)
        return False

def main():
    """Función principal de pruebas"""
    print("🔍 Iniciando pruebas de configuración del chatbot...")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_environment,
        test_database,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    test_names = [
        "Versión de Python",
        "Dependencias",
        "Configuración del entorno",
        "Base de datos",
        "Aplicación Flask"
    ]
    
    all_passed = True
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{i+1}. {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ¡Todas las pruebas pasaron! El chatbot está listo para usar.")
        print("\n📝 Para ejecutar el chatbot:")
        print("   python app.py")
        print("\n📝 Para acceder al chatbot:")
        print("   http://localhost:5000")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n🔧 Soluciones comunes:")
        print("   - Instala las dependencias: pip install -r requirements.txt")
        print("   - Verifica que Python 3.7+ esté instalado")
        print("   - Asegúrate de estar en el directorio correcto del proyecto")

if __name__ == "__main__":
    main() 