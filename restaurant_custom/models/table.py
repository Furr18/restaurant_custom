from odoo import models, fields, api

class Table(models.Model):
    _name = 'restaurant.table'
    _description = 'Restaurant Table'

    name = fields.Char(string='Table Name', required=True)
    capacity = fields.Integer(string='Capacity', required=True)
    is_available = fields.Boolean(string='Is Available', default=True)
    
    @api.model
    def get_available_tables(self):
        # Mengambil semua tabel yang kosong
        return self.search([('is_available', '=', True)])
