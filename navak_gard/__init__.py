from flask import Blueprint

gard = Blueprint(
              "gard",
                 __name__,
                    static_folder="static",
                        template_folder="templates")

import navak_gard.views
import navak_gard.models