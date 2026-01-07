import os
import sys
from modules.paths_internal import models_path, script_path, data_path, extensions_dir, extensions_builtin_dir, cwd  # noqa: F401

import modules.safe  # noqa: F401


def mute_sdxl_imports():
    """create fake modules that SDXL wants to import but doesn't actually use for our purposes"""

    class Dummy:
        pass

    module = Dummy()
    module.LPIPS = None
    sys.modules['taming.modules.losses.lpips'] = module

    module = Dummy()
    module.StableDataModuleFromConfig = None
    sys.modules['sgm.data'] = module
    
    # Redirect taming imports to vendored version in extensions-builtin/LDSR
    ldsr_path = os.path.join(script_path, 'extensions-builtin/LDSR')
    if os.path.exists(ldsr_path) and os.path.exists(os.path.join(ldsr_path, 'vqvae_quantize.py')):
        sys.path.insert(0, ldsr_path)
        try:
            import vqvae_quantize
            taming_modules = Dummy()
            taming_modules.modules = Dummy()
            taming_modules.modules.vqvae = Dummy()
            taming_modules.modules.vqvae.quantize = vqvae_quantize
            sys.modules['taming'] = taming_modules
            sys.modules['taming.modules'] = taming_modules.modules
            sys.modules['taming.modules.vqvae'] = taming_modules.modules.vqvae
            sys.modules['taming.modules.vqvae.quantize'] = vqvae_quantize
            sys.path.pop(0)
        except ImportError as e:
            sys.path.pop(0)
            print(f"Warning: Could not load vendored taming module: {e}", file=sys.stderr)
    
    # Load ldm.modules.midas stub for depth model support
    try:
        sys.path.insert(0, script_path)
        import ldm_midas_stub
        # Register just the midas API module - ldm will be imported separately
        # We register a placeholder that will be merged with the real ldm.modules when it loads
        sys.modules['ldm_midas_stub'] = ldm_midas_stub
        sys.path.pop(0)
    except ImportError as e:
        sys.path.pop(0)
        print(f"Warning: Could not load midas stub module: {e}", file=sys.stderr)


# data_path = cmd_opts_pre.data
sys.path.insert(0, script_path)

# search for directory of stable diffusion in following places
sd_path = None
possible_sd_paths = [os.path.join(script_path, 'repositories/stable-diffusion-stability-ai'), '.', os.path.dirname(script_path)]
for possible_sd_path in possible_sd_paths:
    if os.path.exists(os.path.join(possible_sd_path, 'ldm/models/diffusion/ddpm.py')):
        sd_path = os.path.abspath(possible_sd_path)
        break

assert sd_path is not None, f"Couldn't find Stable Diffusion in any of: {possible_sd_paths}"

mute_sdxl_imports()

path_dirs = [
    (sd_path, 'ldm', 'Stable Diffusion', []),
    (os.path.join(sd_path, '../generative-models'), 'sgm', 'Stable Diffusion XL', ["sgm"]),
    (os.path.join(sd_path, '../BLIP'), 'models/blip.py', 'BLIP', []),
    (os.path.join(sd_path, '../k-diffusion'), 'k_diffusion/sampling.py', 'k_diffusion', ["atstart"]),
]

paths = {}

for d, must_exist, what, options in path_dirs:
    must_exist_path = os.path.abspath(os.path.join(script_path, d, must_exist))
    if not os.path.exists(must_exist_path):
        print(f"Warning: {what} not found at path {must_exist_path}", file=sys.stderr)
    else:
        d = os.path.abspath(d)
        if "atstart" in options:
            sys.path.insert(0, d)
        elif "sgm" in options:
            # Stable Diffusion XL repo has scripts dir with __init__.py in it which ruins every extension's scripts dir, so we
            # import sgm and remove it from sys.path so that when a script imports scripts.something, it doesbn't use sgm's scripts dir.

            sys.path.insert(0, d)
            import sgm  # noqa: F401
            sys.path.pop(0)
        else:
            sys.path.append(d)
        paths[what] = d


# After adding LDM to sys.path, inject the midas stub into ldm.modules
if 'Stable Diffusion' in paths:
    try:
        import ldm  # noqa: F401
        import ldm.modules  # noqa: F401
        import ldm_midas_stub  # noqa: F401
        ldm.modules.midas = ldm_midas_stub
        sys.modules['ldm.modules.midas'] = ldm_midas_stub
        sys.modules['ldm.modules.midas.api'] = ldm_midas_stub.api
    except Exception as e:
        print(f"Warning: Could not inject midas into ldm.modules: {e}", file=sys.stderr)
    
    # Inject ldm.data.util stub for depth preprocessing
    try:
        import ldm.data  # noqa: F401
        import ldm_data_util_stub  # noqa: F401
        ldm.data.util = ldm_data_util_stub
        sys.modules['ldm.data.util'] = ldm_data_util_stub
    except Exception as e:
        print(f"Warning: Could not inject data.util into ldm.data: {e}", file=sys.stderr)

