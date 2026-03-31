from odoo import http
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class FichappController(http.Controller):

    @http.route('/fichapp/recibir_fichaje', type='json', auth='none', methods=['POST'], csrf=False)
    def recibir_fichaje(self, **post):
        data = request.params
        email = data.get('email')
        _logger.info("--- RECIBIENDO FICHAJE PARA: %s ---", email)
        
        # 1. Buscar al empleado
        employee = request.env['hr.employee'].sudo().search([('work_email', '=', email)], limit=1)
        
        _logger.info("EMPLEADO ENCONTRADO: %s", employee.name if employee else "NO ENCONTRADO")

        if not employee:
            return {"status": "error", "message": f"Empleado {email} no encontrado"}
        # 2. Buscar fichaje abierto
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_out', '=', False)
        ], limit=1)

        if not attendance:
            # ENTRADA
            new_record = request.env['hr.attendance'].sudo().create({
                'employee_id': employee.id,
                'check_in': datetime.now(),
            })
            # FORZAR GUARDADO
            request.env.cr.commit() 
            return {"status": "success", "action": "entrada", "employee": employee.name}
        else:
            # SALIDA
            attendance.sudo().write({'check_out': datetime.now()})
            # FORZAR GUARDADO
            request.env.cr.commit()
            return {"status": "success", "action": "salida", "employee": employee.name}