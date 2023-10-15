from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class Warp(models.Model):
    _name = 'sr.warp'
    _description = 'Warp'

    uid = fields.Char('User ID')
    gacha_id = fields.Char('Banner ID')
    gacha_type = fields.Char('Banner Type')
    item_id = fields.Char('Item ID')
    count = fields.Char('Count')
    time = fields.Datetime('Time')
    name = fields.Char('Name')
    lang = fields.Char('Lang')
    item_type = fields.Char('Item Type')
    rank_type = fields.Integer('Rarity')
    wid = fields.Char('Warp ID', index=True)

    banner_id = fields.Many2one('sr.banner', compute='_compute_warp_banner')

    _sql_constraints = [
        ('warp_key', 'UNIQUE (wid)',  'You can not have two warps with the same ID')
    ]

    def _compute_warp_banner(self):
        for warp in self:
            sr_banner = self.env['sr.banner'].search([('banner_key','=',warp.gacha_id)])
            if not sr_banner:
                sr_banner = self.env['sr.banner'].create({
                    'banner_key': warp.gacha_id,
                    'gacha_type_id': warp.gacha_type,
                })
            warp.banner_id = sr_banner

    def _warp_exists(self, wid):
        self.env.cr.execute(f"SELECT 1 FROM sr_warp WHERE wid='{wid}'")
        return self.env.cr.fetchone()

    def generate_warps(self, vals_list):
        for i in range(len(vals_list)):
            id = vals_list[i]['id']
            if not self._warp_exists(id):
                vals_list = vals_list[:i]
                _logger.info("CHECK LIST BREAK" + vals_list)
                break
        _logger.info(vals_list)
        warps = self.create(vals_list)
        _logger.debug(warps)
        return warps[-1]['wid']

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'time' in vals:
                vals['time'] = datetime.strptime(vals['time'], "%Y-%m-%d %H:%M:%S") + timedelta(hours=+5)
            if 'id' in vals:
                vals['wid'] = vals.pop('id')
        
        return super(Warp, self).create(vals_list)



class BannerType(models.Model):
    _name = 'sr.banner.type'
    _description = 'Warp Banner Type'

    name = fields.Char('Name')
    gacha_type = fields.Char('Banner Type')


class Banner(models.Model):
    _name = 'sr.banner'
    _description = 'Warp Banner'

    name = fields.Char('Name', default='~')
    banner_key = fields.Char('Banner ID')
    gacha_type_id = fields.Many2one('sr.banner.type')

    _sql_constraints = [
        ('banner_key', 'UNIQUE (banner_key)',  'You can not have two banners with the same key')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        return super(Banner, self).create(vals_list)