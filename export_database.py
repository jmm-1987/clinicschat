#!/usr/bin/env python3
"""
Script para exportar la base de datos de citas a CSV
"""

import csv
import os
from datetime import datetime
from app import app, db, Cita

def export_to_csv():
    """Exporta todas las citas a un archivo CSV"""
    
    with app.app_context():
        # Obtener todas las citas
        citas = Cita.query.order_by(Cita.fecha_creacion.desc()).all()
        
        # Crear nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'citas_export_{timestamp}.csv'
        
        # Escribir CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID', 'Nombre', 'Teléfono', 'Email', 'Tipo de Cita', 
                         'Fecha', 'Hora', 'Estado', 'Fecha de Creación']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for cita in citas:
                tipo_cita = 'Revisión General' if cita.tipo_cita == 'revision' else 'Padecimiento'
                
                writer.writerow({
                    'ID': cita.id,
                    'Nombre': cita.nombre,
                    'Teléfono': cita.telefono,
                    'Email': cita.email,
                    'Tipo de Cita': tipo_cita,
                    'Fecha': cita.fecha.strftime('%Y-%m-%d'),
                    'Hora': cita.hora,
                    'Estado': cita.estado,
                    'Fecha de Creación': cita.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        print(f"✅ Base de datos exportada exitosamente a: {filename}")
        print(f"📊 Total de citas exportadas: {len(citas)}")
        
        return filename

def show_stats():
    """Muestra estadísticas de la base de datos"""
    
    with app.app_context():
        total_citas = Cita.query.count()
        citas_pendientes = Cita.query.filter_by(estado='pendiente').count()
        citas_confirmadas = Cita.query.filter_by(estado='confirmada').count()
        citas_canceladas = Cita.query.filter_by(estado='cancelada').count()
        revisiones = Cita.query.filter_by(tipo_cita='revision').count()
        padecimientos = Cita.query.filter_by(tipo_cita='padecimiento').count()
        
        print("\n📈 ESTADÍSTICAS DE LA BASE DE DATOS:")
        print(f"   Total de citas: {total_citas}")
        print(f"   Citas pendientes: {citas_pendientes}")
        print(f"   Citas confirmadas: {citas_confirmadas}")
        print(f"   Citas canceladas: {citas_canceladas}")
        print(f"   Revisiones generales: {revisiones}")
        print(f"   Consultas por padecimiento: {padecimientos}")
        
        if total_citas > 0:
            print(f"\n📅 ÚLTIMAS 5 CITAS:")
            ultimas_citas = Cita.query.order_by(Cita.fecha_creacion.desc()).limit(5).all()
            for cita in ultimas_citas:
                tipo = 'Revisión' if cita.tipo_cita == 'revision' else 'Padecimiento'
                print(f"   {cita.fecha_creacion.strftime('%d/%m/%Y %H:%M')} - {cita.nombre} ({tipo})")

if __name__ == "__main__":
    print("🗄️  EXPORTADOR DE BASE DE DATOS")
    print("=" * 40)
    
    # Verificar que existe la base de datos
    if not os.path.exists('citas.db'):
        print("❌ Error: No se encontró la base de datos 'citas.db'")
        print("   Asegúrate de que la aplicación se haya ejecutado al menos una vez.")
        exit(1)
    
    # Mostrar estadísticas
    show_stats()
    
    # Preguntar si quiere exportar
    print("\n¿Quieres exportar la base de datos a CSV? (s/n): ", end="")
    respuesta = input().lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            filename = export_to_csv()
            print(f"\n✅ Exportación completada: {filename}")
        except Exception as e:
            print(f"❌ Error durante la exportación: {e}")
    else:
        print("❌ Exportación cancelada.") 