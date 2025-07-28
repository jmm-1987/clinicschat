#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de la base de datos
"""

from app import app, db, Cita
from datetime import datetime, timedelta

def test_database():
    """Prueba la creación de la base de datos y algunas operaciones básicas"""
    
    with app.app_context():
        # Crear la base de datos
        db.create_all()
        print("✅ Base de datos creada exitosamente")
        
        # Verificar que la tabla existe
        try:
            # Intentar crear una cita de prueba
            cita_prueba = Cita(
                nombre="Paciente Prueba",
                telefono="+34 600 000 000",
                email="prueba@test.com",
                tipo_cita="revision",
                fecha=datetime.now().date() + timedelta(days=1),
                hora="10:00"
            )
            
            db.session.add(cita_prueba)
            db.session.commit()
            print("✅ Cita de prueba creada exitosamente")
            
            # Verificar que se puede leer
            citas = Cita.query.all()
            print(f"✅ Se encontraron {len(citas)} citas en la base de datos")
            
            # Limpiar la cita de prueba
            db.session.delete(cita_prueba)
            db.session.commit()
            print("✅ Cita de prueba eliminada")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        print("✅ Todas las pruebas de base de datos pasaron exitosamente")
        return True

if __name__ == "__main__":
    test_database() 