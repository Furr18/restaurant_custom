from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class Reservation(models.Model):
    _name = 'restaurant.reservation'
    _description = 'Restaurant Reservation'

    reservation_code = fields.Char(string='Reservation Code', required=True, copy=False, readonly=True, default='Reservation Code')
    name = fields.Char(string='Customer Name', required=True)
    email = fields.Char(string='Email')
    reservation_lines = fields.One2many('reservation.line', 'reservation_id', string=".")
    date_start = fields.Datetime(string="Start Time", compute='_compute_date_start', store=True)
    date_end = fields.Datetime(string="End Time", compute='_compute_date_end', store=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', required=True)
    

    @api.depends('reservation_lines.date_start')
    def _compute_date_start(self):
        for record in self:
            record.date_start = min(record.reservation_lines.mapped('date_start'), default=False)

    @api.depends('reservation_lines.date_end')
    def _compute_date_end(self):
        for record in self:
            record.date_end = max(record.reservation_lines.mapped('date_end'), default=False)

    @api.constrains('reservation_lines')
    def _check_date_ranges(self):
        for record in self:
            table_ids = record.reservation_lines.mapped('table.id')
            for line in record.reservation_lines:
                # Cek apakah waktu reservasi dimulai di masa depan
                if line.date_start >= line.date_end:
                    raise ValidationError('The start time must be before the end time.')
                if line.date_start < fields.Datetime.now():
                    raise ValidationError('Start time must be in the future.')

                reservation_start = line.date_start
                reservation_end = line.date_end

                # Mencari reservasi lain yang tumpang tindih
                overlapping_reservations = self.env['restaurant.reservation'].search([
                    ('id', '!=', record.id),  # Jangan memeriksa reservasi yang sedang diedit
                    ('status', '!=', 'cancelled'),  # Abaikan reservasi yang dibatalkan
                    ('reservation_lines.table', 'in', table_ids),  # Sama dengan meja yang dipilih
                    '|',  # Mulai operasi OR
                        '&',  # Kondisi AND pertama
                            ('reservation_lines.date_start', '<', reservation_end),  # Reservasi dimulai sebelum reservasi baru berakhir
                            ('reservation_lines.date_end', '>', reservation_start),  # Reservasi berakhir setelah reservasi baru dimulai
                        '&',  # Kondisi AND kedua (untuk memastikan kondisi kedua OR)
                            ('reservation_lines.date_start', '>=', reservation_end),  # Pastikan reservasi lain tidak dimulai setelah reservasi baru berakhir
                            ('reservation_lines.date_end', '<=', reservation_start)   # Pastikan reservasi lain tidak berakhir sebelum reservasi baru dimulai
                ])


                # Jika ada tumpang tindih waktu, tampilkan pesan error
                if overlapping_reservations:
                    booked_tables = ', '.join(overlapping_reservations.mapped('reservation_lines.table.name'))
                    raise ValidationError(f'The following tables are already booked : {booked_tables}')

    @api.model
    def create(self, vals):
        # Generate reservation code
        if vals.get('reservation_code', 'Reservation Code') == 'Reservation Code':
            sequence_code = self.env['ir.sequence'].next_by_code('restaurant.reservation') or '/'
            vals['reservation_code'] = sequence_code
        return super(Reservation, self).create(vals)

    def unlink(self):
        # Call super to ensure that the delete happens
        res = super(Reservation, self).unlink()
        # Check if there are any remaining records
        if not self.search([]):
            # Reset the sequence
            sequence = self.env['ir.sequence'].search([('code', '=', 'restaurant.reservation')], limit=1)
            if sequence:
                sequence.write({'number_next': 1})  # Reset the sequence to 1
        return res

    def action_confirm(self):
        """Confirm the reservation."""
        self.write({'status': 'confirmed'})

    def action_cancel(self):
        """Cancel the reservation."""
        self.write({'status': 'cancelled'})

    def action_back_to_pending(self):
        """Set status back to pending."""
        self.write({'status': 'pending'})    


class ReservationLine(models.Model):
    _name = 'reservation.line'

    reservation_id = fields.Many2one('restaurant.reservation', string="Customer Name")
    date_start = fields.Datetime(string="Start Time", required=True)
    date_end = fields.Datetime(string="End Time", required=True)
    guest = fields.Char(string="Number of Guests", required=True)
    table = fields.Many2one('restaurant.table', string="Table", required=True)
    note = fields.Text(string="Notes")

    # @api.constrains('date_start', 'date_end')
    # def _check_dates(self):
    #     for line in self:
    #         if line.date_start >= line.date_end:
    #             raise ValidationError('The start time must be before the end time.')
    #         if line.date_start < fields.Datetime.now():
    #             raise ValidationError('The start time must be in the future.')
