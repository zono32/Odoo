from odoo import http
from odoo.http import request
from datetime import datetime
import logging
import requests
import werkzeug

_logger = logging.getLogger(__name__)


class FichappController(http.Controller):

    @http.route('/fichapp/recibir_fichaje', type='json', auth='none',
                methods=['POST'], csrf=False)
    def recibir_fichaje(self, **post):
        data = request.params
        email = data.get('email')
        _logger.info("--- RECIBIENDO FICHAJE PARA: %s ---", email)
        
        # 1. Buscar al empleado
        employee = request.env['hr.employee'].sudo().search([('work_email', '=', email)], limit=1)
        
        _logger.info("EMPLEADO ENCONTRADO: %s",
                     employee.name if employee else "NO ENCONTRADO")

        if not employee:
            return {"status": "error",
                    "message": f"Empleado {email} no encontrado"}
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

    @http.route('/fichapp/auto_login', type='http', auth='user', website=True)
    def auto_login(self, **kw):
        user = request.env.user
        email = user.email or user.login
        name = user.name
        
        api_url = request.env['ir.config_parameter'].sudo().get_param(
            'fichapp.api_url', 'http://localhost:4000')
        vue_url = request.env['ir.config_parameter'].sudo().get_param(
            'fichapp.vue_url', 'http://localhost:5173')

        api_key = (
            'APwXk+7JM7yvqHNNGeeBj8XSRq!$U*@-zKVtQfp_97DJL-bJ3vcW!!AfaTn!eBX'
            '47cYk+BPRa94p%e3ZEs2hpV2K=hrwcHsJasZLhX7ycgd6JJ+u4rw?eezAPKUv^T'
            'rB2aQXcJSj+Tv#nkL*CF+pm5gx$xGwSznZNZF#VZvfEmnMQ-KuM$D5zADEPS&V*'
            'Hah!DgE#-4qB7c25XaDnve_66a=WVBJtjrY^GUMztbuW3_2SdxfUs!TjuBL&Q$5'
            '!gHU'
        )
        headers = {'api-key': api_key}
        
        try:
            # Determinar rol: administrador si tiene grupo system o la etiqueta "admin" en su ficha
            is_admin_group = request.env.user.has_group('base.group_system')

            # Buscamos al empleado para revisar sus etiquetas (categorías)
            employee = request.env['hr.employee'].sudo().search(
                [('work_email', '=', email)], limit=1)
            is_admin_tag = any(
                tag.name and tag.name.lower() == 'admin'
                for tag in employee.category_ids
            ) if employee else False

            role = 'admin' if (is_admin_group or is_admin_tag) else 'user'
            _logger.info("FICHA_LOG: SSO para %s - group: %s, tag: %s -> %s",
                         email, is_admin_group, is_admin_tag, role)

            # Pedimos a Fichapp-Back el Súper-Token
            endpoint = f"{api_url}/api/odoo/sso/{email}?name={name}&role={role}"
            response = requests.get(endpoint, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    return werkzeug.utils.redirect(
                        f"{vue_url}/login?token={token}")
        except Exception as e:
            _logger.error("Error en SSO Fichapp: %s", str(e))

        return werkzeug.utils.redirect(f"{vue_url}/login")