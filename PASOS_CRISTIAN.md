# Las claves de la IA: lo que tienes que hacer tú (unos 30 minutos)

Son solo los pasos que no puedo hacer yo: crear cuentas, meter contraseñas y claves, y pagar o poner tarjeta.
Mientras tanto, yo escribo el programa, las instrucciones del redactor y las portadas.

**Hazlos en orden. Cuando acabes cada bloque, dímelo en una línea** («hecho el 2»). Si algo no sale como dice
aquí, para ese bloque, sáltalo y sigue con el siguiente.

Antes de empezar, contéstame las cuatro preguntas del chat.

---

## 1. Correo nuevo (5 min)

1. Crea una cuenta de Gmail nueva, solo para el canal. Propuesta: `lasclavesdelaia@gmail.com`. Si está cogido,
   prueba con `clavesdelaia.canal@gmail.com`.
2. Activa la verificación en dos pasos.
3. Este correo saldrá público en el feed: no lo uses para nada más.

## 2. GitHub: la casa del pódcast (5 min)

GitHub guarda gratis la página, la lista de episodios y los audios.

- **Si ya tienes cuenta de GitHub:**
  1. Entra y crea una **organización** gratuita: arriba a la derecha, tu foto › Your organizations › New
     organization › Free. Nombre: `lasclavesdelaia`. Correo: el nuevo.
  2. Dentro de la organización, crea un repositorio **público**, vacío, llamado `canal`.
- **Si no tienes cuenta:** crea una con el correo nuevo. Usuario: `lasclavesdelaia`. Después crea el repositorio
  público `canal` en esa cuenta.

## 3. Dejar que Claude escriba solo ahí (3 min)

1. Abre <https://github.com/apps/claude> y pulsa Install (o Configure, si ya estaba).
2. Elige la organización (o la cuenta) `lasclavesdelaia`.
3. Marca **«Only select repositories»** y elige solo `canal`.

Así, la tarea de cada mañana solo puede tocar ese repositorio.

## 4. Que nunca te cobren cuota de más (1 min)

En <https://claude.ai/settings/usage>, deja los **créditos de uso desactivados**. Así, si un día no queda cuota, ese
día no sale el episodio y no se cobra nada.

## 5. La voz: Google Cloud (10 min)

Es la parte más larga. La voz es gratis hasta 1 millón de caracteres al mes, y usaremos menos de la mitad. Pero Google
pide tarjeta.

1. Con el **correo nuevo**, entra en <https://console.cloud.google.com> y acepta las condiciones.
2. Crea un proyecto llamado `voz-claves`.
3. Activa la facturación con tu tarjeta.
4. En «Facturación › Presupuestos y alertas», crea un presupuesto de **1 €** con aviso por correo al 50 % y al 100 %.
5. Busca «Text-to-Speech API» y pulsa **Habilitar**.
6. En «APIs y servicios › Credenciales», crea una **clave de API**. En «Restricciones de API», marca solo
   **Cloud Text-to-Speech API**.
7. Copia la clave. Sin dármela a mí, pégala en GitHub:
   1. ve a `canal` › Settings › Environments › New environment, y llámalo `publicar`;
   2. en «Deployment branches», elige **Selected branches** y añade solo `main`;
   3. en «Environment secrets», pulsa Add secret: nombre `GOOGLE_TTS_KEY`, valor la clave.

Esa clave solo vive en GitHub. La tarea que lee internet nunca la ve. Además, el programa no generará voz si el mes
pasa de 900.000 caracteres.

## 6. La dirección en tu web (3 min)

En Hostinger, entra en «Dominios › cristiansdrojek.com › DNS / Nameservers».

1. Añade un registro nuevo (**no cambies ninguno de los que ya hay**: tu correo depende de ellos):
   - tipo: `CNAME`;
   - nombre: `claves`;
   - destino: `lasclavesdelaia.github.io`;
   - TTL: el que venga.
2. Guarda.

La dirección del pódcast será `claves.cristiansdrojek.com`.

## 7. El canal de YouTube (5 min)

1. Con el **correo nuevo**, entra en YouTube y crea el canal: «Las claves de la IA».
2. En <https://www.youtube.com/verify>, verifica el teléfono. Hace falta para episodios de más de 15 minutos y para
   dar de alta el pódcast.

El alta del pódcast por RSS se hace **más adelante**, cuando ya haya dos o tres episodios. Te avisaré: son 10 minutos.

## 8. Opcional: Artificial Analysis (3 min)

Su ranking solo se puede leer con su API gratuita.

1. Con el correo nuevo, crea una cuenta gratuita en <https://artificialanalysis.ai> y genera una clave de API.
2. Guárdala en tu gestor de contraseñas. Te diré dónde pegarla cuando montemos la tarea de la mañana.

Si lo dejas para otro día, el pódcast cuenta los rankings cuando los publique la prensa o el propio laboratorio.

---

Cuando termines: el 1 y el 7 los hace solo tu cuenta; el 2, 3, 5 y 6 los compruebo yo con una sesión limpia.

## Voz Gemini 3.8 para semanales y especiales (rama `claude/voz-gemini`, 8 oct 2026)

Solo si decides seguir. Tú creas la cuenta y la clave; Claude nunca las toca.

1. Abre console.cloud.google.com con el proyecto **voz-claves** elegido arriba.
2. Menú › **IAM y administración › Cuentas de servicio** › **Crear cuenta de servicio**.
   Nombre: `voz-gemini`. Pulsa **Crear y continuar**.
3. En «Otorgar acceso», elige solo el rol **Usuario de Agent Platform** (en inglés, «Agent Platform User»;
   si aún sale con el nombre viejo, «Vertex AI User», `roles/aiplatform.user`). Ningún otro. **Listo**.
4. Entra en la cuenta `voz-gemini` › pestaña **Claves** › **Agregar clave › Crear clave nueva › JSON**.
   Se descarga un archivo .json. No lo abras ni lo copies a ningún otro sitio.
5. En GitHub: repositorio `lasclavesdelaia/canal` › **Settings › Environments › publicar** ›
   **Environment secrets › Add secret**. Nombre: `GOOGLE_VOZ_GEMINI_SA`. Valor: pega el contenido entero del .json.
6. Borra el .json del Mac (y vacía la papelera) cuando GitHub lo haya guardado.
7. **Tope duro** (recomendado): Facturación › **Presupuestos y alertas** › Crear presupuesto ›
   tipo **Spend cap** (tope de gasto), proyecto voz-claves, servicio **Agent Platform**, mensual.
   Importe: **10 $** mientras duren los créditos (el tope cuenta el coste bruto, sin descontar créditos;
   con menos se pararía aunque pagaran los créditos). Desde el 7 ene 2027, lo que quieras pagar al mes.
8. Dile a Claude «fusiona la voz Gemini». Fusionar antes del paso 5 rompería la publicación.
