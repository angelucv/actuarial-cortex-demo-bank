# Demo de Actuarial Cortex — Subir a GitHub y desplegar desde ahí

El código está en GitHub y preparado con el workflow de sincronización al Space en Hugging Face.

## Cambiar nombre/URL del Space (actuarial-cortex-bank-fraud)

Para usar la URL **angelucv-actuarial-cortex-bank-fraud.hf.space**:

1. En [huggingface.co/spaces](https://huggingface.co/spaces) crea un **Space nuevo**.
2. **Name:** `actuarial-cortex-bank-fraud` (así la URL será `https://angelucv-actuarial-cortex-bank-fraud.hf.space`).
3. **SDK:** Docker. Crear el Space (puede quedar vacío).
4. El workflow de este repo ya apunta a ese nombre; con el siguiente push a `main` (o ejecutando el Action a mano) se subirá el código al nuevo Space.
5. Opcional: borra el Space antiguo **NovaBank_Angel** en HF si ya no lo usas.

Si en tu PC tienes el remote `hf` apuntando al Space viejo y quieres hacer push manual al nuevo:

```bash
git remote set-url hf https://huggingface.co/spaces/angelucv/actuarial-cortex-bank-fraud
git push hf main
```

## Repositorio

- **GitHub:** [angelucv/actuarial-cortex-demo-bank](https://github.com/angelucv/actuarial-cortex-demo-bank)
- **Código local:** `C:\Users\Angel\NovaBank_Angel` (carpeta clonada desde el Space HF).

## Sincronización automática con Hugging Face

En el repo de GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- **Name:** `HF_TOKEN`
- **Secret:** tu token de Hugging Face (permiso **Write**), desde [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

A partir de ahí, cada **push a `main`** actualizará el Space [angelucv/actuarial-cortex-bank-fraud](https://huggingface.co/spaces/angelucv/actuarial-cortex-bank-fraud).

## Remotes

- `origin` → [actuarial-cortex-demo-bank](https://github.com/angelucv/actuarial-cortex-demo-bank)
- `hf` → [actuarial-cortex-bank-fraud](https://huggingface.co/spaces/angelucv/actuarial-cortex-bank-fraud) (push manual: `git push hf main`)
