from openerp.osv import fields, osv

class rdm_customer_point(osv.osv):
    _name = 'rdm.customer.point'
    _description = 'Redemption Customer Point'
    
    _columns = {
        'customer_id': fields.many2one('rdm.customer','Customer', required=True),
        'trans_id': fields.integer('Transaction ID', readonly=True),
        'reward_trans_id': fields.integer('Reward Transaction ID', readonly=True),
        'trans_type': fields.selection([('promo','Promotion'),('point','Point'),('reward','Reward'),('deduct','Deduct'),('reference','Reference'),('member','New Member')], 'Transaction Type'),        
        'point': fields.integer('Point #'),
        'expired_date': fields.date('Expired Date'),
        'deleted': fields.boolean('Deleted'),        
    }        
    
rdm_customer_point()
