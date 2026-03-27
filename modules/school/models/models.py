from odoo import models, fields, api
from datetime import date

class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Estudiante de la escuela'

    name = fields.Char(string='Nombre', required=True)
    birth_date = fields.Date(string='Fecha de Nacimiento')
    
    # Modificamos el campo age para que sea computado
    age = fields.Integer(string='Edad', compute='_compute_age', store=True)
    
    grade = fields.Char(string='Grado/Curso')
    description = fields.Text(string='Notas adicionales')

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                birth = record.birth_date
                # Cálculo de edad estándar
                record.age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            else:
                record.age = 0