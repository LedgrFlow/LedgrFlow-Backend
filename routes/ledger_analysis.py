from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.file import File
from utils.temp_file_manager import TempFileManager
from hook.ledger_parser import (
    parse_ledger,
    calculates_ledger,
    analyze_ledger,
    analyze_ledger_compare,
    analyze_ledger_alerts,
)
from utils.validates import has_any_value
from marshmallow import ValidationError
import uuid
import os

# Importar las clases de ledger-cli-toolkit
try:
    from ledger_cli import LedgerParser, LedgerAnalyst

except ImportError as e:
    # Fallback si no está instalada la librería
    LedgerParser = None
    LedgerAnalyst = None

ledger_analysis_bp = Blueprint("ledger_analysis", __name__)


# Instanciar el gestor de archivos temporales
temp_manager = TempFileManager()


def safe_calculation(
    calculation_func,
    *args,
    error_message="Error en cálculo",
    default_value={},
    **kwargs,
):
    """
    Ejecuta una función de cálculo de forma segura, retornando un valor por defecto si falla

    Args:
        calculation_func: Función a ejecutar
        *args: Argumentos posicionales para la función
        error_message: Mensaje de error personalizado
        **kwargs: Argumentos nombrados para la función

    Returns:
        Resultado de la función o diccionario vacío si falla
    """
    try:
        return calculation_func(*args, **kwargs)
    except Exception as e:
        print(f"{error_message}: {e}")
        return default_value


def validate_ledger_library():
    """Verifica que la librería ledger-cli-toolkit esté disponible"""
    if not all([LedgerParser, LedgerAnalyst]):
        raise ImportError("La librería ledger-cli-toolkit no está instalada")


def get_user_file(file_id: str, user_id: str) -> File:
    """
    Obtiene un archivo y verifica que pertenezca al usuario

    Args:
        file_id: ID del archivo
        user_id: ID del usuario

    Returns:
        Objeto File si existe y pertenece al usuario

    Raises:
        ValueError: Si el archivo no existe o no pertenece al usuario
    """
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise ValueError("ID de archivo inválido")

    file = File.query.get(file_uuid)

    if not file:
        raise ValueError("Archivo no encontrado")

    if str(file.user_id) != user_id:
        raise ValueError("Acceso denegado")

    if file.file_extension not in [".ledger"]:
        raise ValueError("El archivo debe ser de tipo .ledger")

    return file


@ledger_analysis_bp.route("/parser/<file_id>", methods=["GET"])
@jwt_required()
def analyze_ledger_parser(file_id):
    """Análisis completo usando LedgerParser"""
    try:
        current_user_id = get_jwt_identity()

        # validar librería
        validate_ledger_library()

        # Obtener archivo
        file = get_user_file(file_id, current_user_id)

        (
            _,
            parser_document,
            transactions,
            accounts,
            accounts_advance,
            metadata,
            parents,
            transactions_resolved,
        ) = parse_ledger(file.file_content, file.file_content)
        (
            balances,
            balances_by_parents,
            state_results,
            balances_by_details,
            period,
        ) = calculates_ledger(file.file_content, file.file_content)

        if has_any_value(
            balances, balances_by_parents, state_results, balances_by_details, period
        ):

            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "transactions_resolved": transactions_resolved,
                            "ledger_document": parser_document,
                            "transactions": transactions,
                            "accounts": accounts,
                            "accounts_advance": accounts_advance,
                            "metadata": metadata,
                            "balances": balances,
                            "balances_by_parents": balances_by_parents,
                            "state_results": state_results,
                            "balances_by_details": balances_by_details,
                            "period": period,
                            "parents": parents,
                        },
                    }
                ),
                200,
            )

        else:
            return jsonify({"error": "No se pudieron calcular los datos"}), 400

    except ImportError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@ledger_analysis_bp.route("/analyst/<file_id>", methods=["GET"])
@jwt_required()
def analyze_ledger_analyst(file_id):
    """Análisis completo usando LedgerAnalyst"""
    try:
        current_user_id = get_jwt_identity()

        # Validar librería
        validate_ledger_library()

        # Obtener archivo
        file = get_user_file(file_id, current_user_id)

        (
            daily,
            pie_expenses,
            pie_incomes,
            assets_summary,
            liabilities_summary,
            balance_by_day,
            accounts_used,
            detected_alerts,
            cashflow_by_month,
            expenses_trends,
            monthly_growth_rates,
            monthly_expense_ratio,
            moving_average,
            trend_slope,
            predicted_months,
            extreme_months,
            classify_months,
            income_dependency,
            cumulative_net_income,
            months,
        ) = analyze_ledger(file=file.file_content, file_accounts=file.file_content)

        if has_any_value(
            daily,
            pie_expenses,
            pie_incomes,
            assets_summary,
            liabilities_summary,
            balance_by_day,
            accounts_used,
            detected_alerts,
            cashflow_by_month,
            expenses_trends,
            monthly_growth_rates,
            monthly_expense_ratio,
            moving_average,
            trend_slope,
            predicted_months,
            extreme_months,
            classify_months,
            income_dependency,
            cumulative_net_income,
            months,
        ):
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {
                            "daily_incomes_expenses": daily,
                            "expenses_pie": pie_expenses,
                            "incomes_pie": pie_incomes,
                            "assets_summary": assets_summary,
                            "liabilities_summary": liabilities_summary,
                            "balance_by_day": balance_by_day,
                            "accounts_used": accounts_used,
                            "detected_alerts": detected_alerts,
                            "cashflow_by_month": cashflow_by_month,
                            "expenses_trends": expenses_trends,
                            "monthly_growth_rates": monthly_growth_rates,
                            "monthly_expense_ratio": monthly_expense_ratio,
                            "moving_average": moving_average,
                            "trend_slope": trend_slope,
                            "predicted_months": predicted_months,
                            "extreme_months": extreme_months,
                            "classify_months": classify_months,
                            "income_dependency": income_dependency,
                            "cumulative_net_income": cumulative_net_income,
                            "months": months,
                        },
                    }
                ),
                200,
            )

        else:
            return jsonify({"error": "No se pudieron analizar los datos"}), 400

    except ImportError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ledger_analysis_bp.route("/compare/<file_id>", methods=["POST"])
@jwt_required()
def compare_months(file_id):
    """Comparar dos meses específicos"""
    try:
        current_user_id = get_jwt_identity()

        # Validar librería
        validate_ledger_library()

        # Obtener parámetros
        data = request.get_json()
        month1 = data.get("month1")
        month2 = data.get("month2")

        if not month1 or not month2:
            return jsonify({"error": "Debe proporcionar month1 y month2"}), 400

        # Obtener archivo
        file = get_user_file(file_id, current_user_id)

        compare_result = analyze_ledger_compare(
            file=file.file_content,
            file_accounts=file.file_content,
            month1=month1,
            month2=month2,
        )

        if compare_result:
            return jsonify({"success": True, "data": compare_result}), 200
        else:
            return jsonify({"error": "No se pudieron comparar los datos"}), 400

    except ImportError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@ledger_analysis_bp.route("/alerts/<file_id>", methods=["POST"])
@jwt_required()
def detect_alerts(file_id):
    """Detectar gastos inusuales con umbral personalizable"""
    try:
        current_user_id = get_jwt_identity()

        # Validar librería
        validate_ledger_library()

        # Obtener umbral
        data = request.get_json() or {}
        threshold = data.get("threshold", 1.5)

        # Obtener archivo
        file = get_user_file(file_id, current_user_id)

        alerts = analyze_ledger_alerts(
            file=file.file_content,
            file_accounts=file.file_content,
            threshold=threshold,
        )

        if alerts:
            return (
                jsonify(
                    {
                        "success": True,
                        "data": {"alerts": alerts, "threshold_used": threshold},
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "No se pudieron analizar los datos"}), 400

    except ImportError as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


@ledger_analysis_bp.route("/cleanup", methods=["POST"])
@jwt_required()
def cleanup_temp_files():
    """Limpiar todos los archivos temporales"""
    try:
        count = temp_manager.cleanup_all_temp_files()
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Se eliminaron {count} archivos temporales",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Error al limpiar archivos temporales"}), 500
