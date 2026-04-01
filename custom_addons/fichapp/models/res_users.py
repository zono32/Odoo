import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Buscamos al empleado vinculado al usuario actual
    employee_id = fields.Many2one(
        'hr.employee', string='Empleado', compute='_compute_employee')

    # Traemos los datos reales de la ficha de empleado
    emp_phone = fields.Char(related='employee_id.work_phone', readonly=True)
    emp_job = fields.Char(related='employee_id.job_title', readonly=True)
    emp_image = fields.Binary(related='employee_id.image_1920', readonly=True)

    # Datos en vivo traídos de Fichapp API
    fichapp_hora_entrada = fields.Char(
        string="Hora Entrada", compute='_compute_fichapp_data')
    fichapp_hora_salida = fields.Char(
        string="Hora Salida", compute='_compute_fichapp_data')
    fichapp_horas_semanales = fields.Char(
        string="Horas Semanales", compute='_compute_fichapp_data')
    fichapp_hora_estimada_salida = fields.Char(
        string="Salida Estimada", compute='_compute_fichapp_data')

    # Sincronización Odoo -> Fichapp
    fichapp_sync_locality = fields.Selection([
        ('685533c6957ee8da913d72df', 'Vigo'),
    ], string="Fichapp Localidad", default='685533c6957ee8da913d72df')

    fichapp_sync_contract = fields.Selection([
        ('685533c6957ee8da913d72f7', 'Anual (22 días)'),
    ], string="Fichapp Contrato", default='685533c6957ee8da913d72f7')

    fichapp_sync_role = fields.Selection([
        ('user', 'Usuario'),
        ('admin', 'Administrador'),
        ('manager', 'Manager'),
    ], string="Fichapp Rol", default='user')

    @api.depends('name')
    def _compute_employee(self):
        for user in self:
            # Busca al empleado que tenga asignado el usuario
            employee = self.env['hr.employee'].search(
                [('user_id', '=', user.id)], limit=1)
            user.employee_id = employee.id if employee else False

    def _compute_fichapp_data(self):
        params = self.env['ir.config_parameter'].sudo()
        api_url = params.get_param('fichapp.api_url', 'http://localhost:4000')
        api_key = (
            "APwXk+7JM7yvqHNNGeeBj8XSRq!$U*@-zKVtQfp_97DJL-bJ3vcW!!AfaTn!eBX"
            "47cYk+BPRa94p%e3ZEs2hpV2K=hrwcHsJasZLhX7ycgd6JJ+u4rw?eezAPKUv^T"
            "rB2aQXcJSj+Tv#nkL*CF+pm5gx$xGwSznZNZF#VZvfEmnMQ-KuM$D5zADEPS&V*"
            "Hah!DgE#-4qB7c25XaDnve_66a=WVBJtjrY^GUMztbuW3_2SdxfUs!TjuBL&Q$5"
            "!gHU"
        )

        for user in self:
            user.fichapp_hora_entrada = "--:--"
            user.fichapp_hora_salida = "--:--"
            user.fichapp_horas_semanales = "0.00"
            user.fichapp_hora_estimada_salida = "--:--"

            # Intentar obtener el email del empleado o del usuario
            email = user.email or (
                user.employee_id and user.employee_id.work_email)
            if not email:
                continue

            try:
                headers = {'api-key': api_key}
                response = requests.get(
                    f"{api_url}/api/odoo/summary/{email}",
                    headers=headers, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    user.fichapp_hora_entrada = data.get(
                        "hora_entrada", "--:--")
                    user.fichapp_hora_salida = data.get(
                        "hora_salida", "--:--")
                    user.fichapp_horas_semanales = data.get(
                        "horas_semanales", "0.00")
                    user.fichapp_hora_estimada_salida = data.get(
                        "hora_estimada_salida", "--:--")
            except Exception as e:
                _logger.error(f"Fichapp API Error para {email}: {str(e)}")

    def action_fichapp_sync(self):
        """Sincroniza los datos del usuario con Fichapp"""
        params = self.env['ir.config_parameter'].sudo()
        api_url = params.get_param('fichapp.api_url', 'http://localhost:4000')
        api_key = (
            "APwXk+7JM7yvqHNNGeeBj8XSRq!$U*@-zKVtQfp_97DJL-bJ3vcW!!AfaTn!eBX"
            "47cYk+BPRa94p%e3ZEs2hpV2K=hrwcHsJasZLhX7ycgd6JJ+u4rw?eezAPKUv^T"
            "rB2aQXcJSj+Tv#nkL*CF+pm5gx$xGwSznZNZF#VZvfEmnMQ-KuM$D5zADEPS&V*"
            "Hah!DgE#-4qB7c25XaDnve_66a=WVBJtjrY^GUMztbuW3_2SdxfUs!TjuBL&Q$5"
            "!gHU"
        )

        for user in self:
            email = user.email or (
                user.employee_id and user.employee_id.work_email)
            if not email:
                continue

            payload = {
                'username': email.lower(),
                'name': user.name,
                'role': user.fichapp_sync_role,
                'locality_id': user.fichapp_sync_locality,
                'contract_type_id': user.fichapp_sync_contract
            }

            try:
                headers = {'api-key': api_key}
                response = requests.post(
                    f"{api_url}/api/odoo/users/sync",
                    json=payload, headers=headers, timeout=5)
                if response.status_code == 200:
                    _logger.info(f"Fichapp Sync Success: {email}")
                else:
                    _logger.error(
                        f"Fichapp Sync Failed for {email}: {response.text}")
            except Exception as e:
                _logger.error(
                    f"Error sincronizando {email} con Fichapp: {str(e)}")