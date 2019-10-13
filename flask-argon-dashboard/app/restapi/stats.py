# -*- encoding: utf-8 -*-
"""
Argon Dashboard - coded in Flask

Author  : AppSeed App Generator
Design  : Creative-Tim.com
License : MIT 
Support : https://appseed.us/support 
"""

from flask_restful import Resource

from app.models    import Measurement

class ApiStats(Resource):

    def get(self,segment):
        return {'err': 'unknown'}, 404
        # See the model for details 
        # val = Stats( segment ).val 

        # if 'traffic' == segment:
        #     return { segment : val }, 200

        # elif 'users' == segment:        
        #     return { segment : val }, 200

        # elif 'sales' == segment:        
        #     return { segment : val }, 200

        # elif 'perf' == segment:        
        #     return { segment : val }, 200

        # else:
        #     return {'err': 'unknown'}, 404
            