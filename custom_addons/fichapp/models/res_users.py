from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Buscamos al empleado vinculado al usuario actual
    employee_id = fields.Many2one('hr.employee', string='Empleado', compute='_compute_employee')
    
    # Traemos los datos reales de la ficha de empleado
    emp_phone = fields.Char(related='employee_id.work_phone', readonly=True)
    emp_job = fields.Char(related='employee_id.job_title', readonly=True)
    emp_image = fields.Binary(related='employee_id.image_1920', readonly=True)

    @api.depends('name')
    def _compute_employee(self):
        for user in self:
            # Esta línea busca al empleado que tenga asignado el usuario en la pestaña Ajustes
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            user.employee_id = employee.id if employee else False