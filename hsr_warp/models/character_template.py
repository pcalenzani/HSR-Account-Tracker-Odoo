from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

# Character Template
class CharacterTemplate(models.Model):
    _name = 'sr.character.template'
    _description = 'Character Template'
    _inherit = 'sr.image.mixin'
    
    avatar = fields.Char("Character Name")
    character_id = fields.Integer('Character ID')
    warp_ids = fields.One2many('sr.warp', 'character_id', string='Warps')

    # -- Element & Path --
    element_id = fields.Many2one('sr.element', string='Element')
    element_img_id = fields.Many2one(related='element_id.img_id', string='Element Image')
    path_id = fields.Many2one('sr.path', string='Path')
    path_img_id = fields.Many2one(related='path_id.img_id', string='Path Image')

    # -- Character Images --
    portrait_img_id = fields.Many2one('ir.attachment', string='Portrait Image', compute='_compute_images',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','portrait_img_id')]")
    preview_img_id = fields.Many2one('ir.attachment', string='Preview Image', compute='_compute_images',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','preview_img_id')]")
    icon_img_id = fields.Many2one('ir.attachment', string='Icon Image', compute='_compute_images',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','icon_img_id')]")

    _sql_constraints = [
        ('character_key', 'UNIQUE (character_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]

    @api.depends('avatar')
    def _compute_display_name(self):
        # Compute name, example: Dan (Template)
        for rec in self:
            rec.display_name = f"{rec.avatar} (Template)"

    @api.depends('character_id')
    def _compute_images(self):
        # Get image attachments for each image type when character id updated
        for rec in self:
            portrait_img_path = '/hsr_warp/static/image/character_portrait/'
            rec.portrait_img_id = rec.get_image_from_path(portrait_img_path,
                                                           rec.character_id,
                                                           field='portrait_img_id').id
            preview_img_path = '/hsr_warp/static/image/character_preview/'
            rec.preview_img_id = rec.get_image_from_path(preview_img_path,
                                                          rec.character_id,
                                                          field='preview_img_id').id
            icon_img_path = '/hsr_warp/static/icon/character/'
            rec.icon_img_id = rec.get_image_from_path(icon_img_path,
                                                       rec.character_id,
                                                       field='icon_img_id').id

    
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args += ['|', ('avatar',operator,name), ('character_id',operator,name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)

        self.env.cr.execute("""SELECT id FROM sr_character_template WHERE character_id in %s LIMIT 1""", [sr_ids])
        ids = tuple(self.env.cr.fetchall())
        return self.__class__(self.env, ids, ids)
    
    # WINDOW ACTIONS
    def action_element(self):
        return {
            'name': 'Character Element',
            'type': 'ir.actions.act_window',
            'res_model': 'sr.element',
            'view_mode': 'form',
            'domain': [('id','=',self.element_id.id)]
        }    
    
    def action_path(self):
        return {
            'name': 'Character Path',
            'type': 'ir.actions.act_window',
            'res_model': 'sr.path',
            'view_mode': 'form',
            'domain': [('id','=',self.path_id.id)]
        }


class Element(models.Model):
    _name = 'sr.element'
    _description = 'Element'
    _inherit = 'sr.image.mixin'

    '''
    ('Wind', 'Wind')
    ('Ice', 'Ice')
    ('Physical', 'Physical')
    ('Fire', 'Fire')
    ('Quantum', 'Quantum')
    ('Lightning', 'Lightning')
    ('Imaginary', 'Imaginary')
    '''
    
    name = fields.Char('Name')
    reference = fields.Char('Internal Ref')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id',
                             domain="[('res_model','=','sr.element'),('res_field','=','img_id')]")
    character_template_ids = fields.One2many('sr.character.template', 'element_id', string='Characters')
    
    @api.depends('name')
    def _compute_img_id(self):
        # Get image attachment when updating name
        img_path = '/hsr_warp/static/icon/element/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path, rec.name).id
    

class Path(models.Model):
    _name = 'sr.path'
    _description = 'Aeon Path'
    _inherit = 'sr.image.mixin'
    
    '''
    ('Warrior', 'Destruction')
    ('Priest', 'Abundance')
    ('Rogue', 'Hunt')
    ('Mage', 'Erudition')
    ('Shaman', 'Harmony')
    ('Warlock', 'Nihility')
    ('Knight', 'Preservation')
    '''
    
    name = fields.Char("Name")
    reference = fields.Char('Internal Ref')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id',
                             domain="[('res_model','=','sr.path'),('res_field','=','img_id')]")
    character_template_ids = fields.One2many('sr.character.template', 'path_id', string='Characters')

    @api.depends('name')
    def _compute_img_id(self):
        # Get image attachment when updating name
        img_path = '/hsr_warp/static/icon/path/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path, rec.name).id
    
