from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.file import File
from schemas.file_schema import (
    FileCreateSchema, FileUpdateSchema, FileResponseSchema, 
    FileResponseWithContentSchema, validate_file_extension
)
from marshmallow import ValidationError
import uuid
import os
from werkzeug.utils import secure_filename

files_bp = Blueprint('files', __name__)

# Instanciar esquemas
file_create_schema = FileCreateSchema()
file_update_schema = FileUpdateSchema()
file_response_schema = FileResponseSchema()
file_response_with_content_schema = FileResponseWithContentSchema()

@files_bp.route('/', methods=['GET'])
@jwt_required()
def get_files():
    """Obtener lista de archivos del usuario actual (con paginación)"""
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limitar per_page a máximo 50
        per_page = min(per_page, 50)
        
        # Filtrar archivos por usuario
        files = File.query.filter_by(user_id=current_user_id).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'files': [file_response_schema.dump(file) for file in files.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': files.total,
                'pages': files.pages,
                'has_next': files.has_next,
                'has_prev': files.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@files_bp.route('/<file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Obtener un archivo específico por ID (con contenido)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validar formato UUID
        try:
            file_uuid = uuid.UUID(file_id)
        except ValueError:
            return jsonify({'error': 'ID de archivo inválido'}), 400
        
        file = File.query.get(file_uuid)
        
        
        if not file:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Verificar que el archivo pertenece al usuario
        if str(file.user_id) != current_user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        return jsonify({
            'file': file_response_with_content_schema.dump(file)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@files_bp.route('/', methods=['POST'])
@jwt_required()
def create_file():
    """Crear un nuevo archivo desde archivo subido o datos JSON"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar si se envió un archivo
        if 'file' in request.files:
            uploaded_file = request.files['file']
            
            if uploaded_file.filename == '':
                return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
            
            # Obtener información del archivo
            filename = secure_filename(uploaded_file.filename)
            file_extension = File.get_file_extension(filename)
            
            if not file_extension:
                return jsonify({'error': 'No se pudo determinar la extensión del archivo'}), 400
            
            # Validar que la extensión esté permitida
            if file_extension not in File.ALLOWED_EXTENSIONS:
                return jsonify({'error': 'Tipo de archivo no permitido. Solo se permiten: .ledger, .md, .txt, .markdown'}), 400
            
            # Leer contenido del archivo
            try:
                file_content = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                return jsonify({'error': 'El archivo no es un archivo de texto válido'}), 400
            
            # Obtener tamaño del archivo
            file_size = len(file_content.encode('utf-8'))
            
        else:
            # Procesar datos JSON como antes
            data = file_create_schema.load(request.json)
            
            filename = data['name']
            file_content = data['file_content']
            
            if not data.get('file_extension'):
                # Si no se proporciona extensión, intentar extraerla del nombre
                file_extension = File.get_file_extension(filename)
                if not file_extension:
                    return jsonify({'error': 'Debe especificar la extensión del archivo'}), 400
            else:
                file_extension = data['file_extension']
            
            # Validar que la extensión esté permitida
            if file_extension not in File.ALLOWED_EXTENSIONS:
                return jsonify({'error': 'Tipo de archivo no permitido. Solo se permiten: .ledger, .md, .txt, .markdown'}), 400
            
            file_size = len(file_content.encode('utf-8'))
        
        # Verificar si ya existe un archivo con el mismo nombre para este usuario
        existing_file = File.query.filter_by(
            user_id=current_user_id, 
            name=filename
        ).first()
        
        if existing_file:
            return jsonify({'error': 'Ya existe un archivo con ese nombre'}), 400
        
        # Crear nuevo archivo
        file = File(
            name=filename,
            file_extension=file_extension,
            file_content=file_content,
            user_id=current_user_id,
            file_size=file_size
        )
        
        # Guardar en base de datos
        db.session.add(file)
        db.session.commit()
        
        return jsonify({
            'message': 'Archivo creado exitosamente',
            'file': file_response_schema.dump(file)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@files_bp.route('/<file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    """Actualizar un archivo"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validar formato UUID
        try:
            file_uuid = uuid.UUID(file_id)
        except ValueError:
            return jsonify({'error': 'ID de archivo inválido'}), 400
        
        file = File.query.get(file_uuid)
        
        if not file:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Verificar que el archivo pertenece al usuario
        if str(file.user_id) != current_user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Validar datos de entrada
        data = file_update_schema.load(request.json, partial=True)
        
        # Verificar si se está cambiando el nombre y si ya existe
        if 'name' in data and data['name'] != file.name:
            existing_file = File.query.filter_by(
                user_id=current_user_id, 
                name=data['name']
            ).first()
            
            if existing_file:
                return jsonify({'error': 'Ya existe un archivo con ese nombre'}), 400
        
        # Actualizar campos
        if 'name' in data:
            file.name = data['name']
        
        if 'file_content' in data:
            file.update_content(data['file_content'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Archivo actualizado exitosamente',
            'file': file_response_schema.dump(file)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@files_bp.route('/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Eliminar un archivo"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validar formato UUID
        try:
            file_uuid = uuid.UUID(file_id)
        except ValueError:
            return jsonify({'error': 'ID de archivo inválido'}), 400
        
        file = File.query.get(file_uuid)
        
        if not file:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Verificar que el archivo pertenece al usuario
        if str(file.user_id) != current_user_id:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({
            'message': 'Archivo eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@files_bp.route('/search', methods=['GET'])
@jwt_required()
def search_files():
    """Buscar archivos por nombre o extensión"""
    try:
        current_user_id = get_jwt_identity()
        
        query = request.args.get('q', '').strip()
        extension = request.args.get('extension', '').strip()
        
        if not query and not extension:
            return jsonify({'error': 'Debe proporcionar un término de búsqueda o extensión'}), 400
        
        # Construir consulta base
        files_query = File.query.filter_by(user_id=current_user_id)
        
        # Aplicar filtros
        if query:
            files_query = files_query.filter(File.name.ilike(f'%{query}%'))
        
        if extension:
            if extension.startswith('.'):
                files_query = files_query.filter(File.file_extension == extension)
            else:
                files_query = files_query.filter(File.file_extension == f'.{extension}')
        
        files = files_query.all()
        
        return jsonify({
            'files': [file_response_schema.dump(file) for file in files],
            'total': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500 