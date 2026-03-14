# Demo de Actuarial Cortex — Subir a GitHub y desplegar desde ahí

El código está en GitHub y preparado con el workflow de sincronización al Space en Hugging Face.

## Repositorio

- **GitHub:** [angelucv/actuarial-cortex-demo-bank](https://github.com/angelucv/actuarial-cortex-demo-bank)
- **Código local:** `C:\Users\Angel\NovaBank_Angel` (carpeta clonada desde el Space HF).

## Sincronización automática con Hugging Face

En el repo de GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- **Name:** `HF_TOKEN`
- **Secret:** tu token de Hugging Face (permiso **Write**), desde [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

A partir de ahí, cada **push a `main`** actualizará el Space [angelucv/NovaBank_Angel](https://huggingface.co/spaces/angelucv/NovaBank_Angel).

## Remotes

- `origin` → [actuarial-cortex-demo-bank](https://github.com/angelucv/actuarial-cortex-demo-bank)
- `hf` → [NovaBank_Angel](https://huggingface.co/spaces/angelucv/NovaBank_Angel) (push manual: `git push hf main`)
