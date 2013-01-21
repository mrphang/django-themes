from os.path import join

from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import find_template

def patched_find_template(name, dirs=None):
    request = getattr(settings, 'request_handler', None)
    if request:
        for prefix in request.theme.template_dir_list:
            try:
                return find_template(join(prefix, name), dirs)
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)
    else:
        return find_template(name, dirs)

if 'coffin' in settings.INSTALLED_APPS:
    from coffin.common import CoffinEnvironment
    from jinja2.exceptions import TemplateNotFound

    def _load_template(self, name, globals):
        request = getattr(settings, 'request_handler', None)
        if request:
            for prefix in request.theme.template_dir_list:
                try:
                    return super(CoffinEnvironment, self)._load_template(join(prefix, name), globals)
                except TemplateNotFound:
                    pass
            TemplateNotFound(name)
        else:
            return super(CoffinEnvironment, self)._load_template(name, globals)


def monkey_patch_template_loaders():
    from django.template import loader
    loader.find_template = patched_find_template
    if 'coffin' in settings.INSTALLED_APPS:
        import types
        from coffin import common
        common.env._load_template = types.MethodType(_load_template, common.env)