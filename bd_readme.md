Perfecto ✅
Tu modelo lógico es una excelente base para un **sistema de gestión financiera inteligente orientado a estudiantes universitarios**, pero con lo que planeas (categorías compartidas, metas conjuntas, gastos personales y grupales, IA financiera, etc.), debemos **escalar la estructura** para soportar multiusuario, colaboración y analítica futura.

---

## 🧩 NUEVO DISEÑO DE TABLAS (versión mejorada y escalable)

### 1. **Usuarios**

Información básica y autenticación.

| Campo            | Tipo                    | Descripción          |
| ---------------- | ----------------------- | -------------------- |
| id_usuario       | SERIAL PK               | Identificador único  |
| nombre           | VARCHAR(100)            | Nombre completo      |
| correo           | VARCHAR(100) UNIQUE     | Email del usuario    |
| contrasena_hash  | VARCHAR(255)            | Contraseña cifrada   |
| moneda_preferida | VARCHAR(10)             | Ej: 'COP', 'USD'     |
| fecha_registro   | TIMESTAMP DEFAULT NOW() | Fecha de creación    |
| foto_perfil      | VARCHAR(255)            | URL o ruta de imagen |
| tipo_usuario     | ENUM('normal','admin')  | Rol del usuario      |

---

### 2. **Grupos**

Permite crear grupos de gastos compartidos (ej: “Casa estudiantes 101”).

| Campo          | Tipo                          | Descripción           |
| -------------- | ----------------------------- | --------------------- |
| id_grupo       | SERIAL PK                     | Identificador         |
| nombre         | VARCHAR(100)                  | Nombre del grupo      |
| descripcion    | TEXT                          | Descripción del grupo |
| fecha_creacion | TIMESTAMP DEFAULT NOW()       | Fecha de creación     |
| creado_por     | INT FK → usuarios(id_usuario) | Creador del grupo     |

---

### 3. **Usuarios_Grupos**

Relación muchos a muchos entre usuarios y grupos.

| Campo       | Tipo                          | Descripción          |
| ----------- | ----------------------------- | -------------------- |
| id_usuario  | INT FK → usuarios(id_usuario) |                      |
| id_grupo    | INT FK → grupos(id_grupo)     |                      |
| rol         | ENUM('miembro','admin')       | Permisos en el grupo |
| fecha_union | TIMESTAMP DEFAULT NOW()       | Cuándo se unió       |

---

### 4. **Categorias**

Soporta categorías por defecto y personalizadas.

| Campo        | Tipo                               | Descripción            |
| ------------ | ---------------------------------- | ---------------------- |
| id_categoria | SERIAL PK                          | Identificador          |
| nombre       | VARCHAR(50)                        | Nombre de categoría    |
| tipo         | ENUM('ingreso','gasto')            | Tipo                   |
| color        | VARCHAR(20)                        | Color de interfaz      |
| icono        | VARCHAR(100)                       | Icono visual           |
| es_global    | BOOLEAN DEFAULT FALSE              | TRUE = visible a todos |
| id_usuario   | INT NULL FK → usuarios(id_usuario) | NULL si es global      |

---

### 5. **Gastos**

Registra los gastos individuales o de grupo.

| Campo        | Tipo                                              | Descripción          |
| ------------ | ------------------------------------------------- | -------------------- |
| id_gasto     | SERIAL PK                                         | Identificador        |
| descripcion  | VARCHAR(255)                                      | Detalle              |
| monto        | DECIMAL(12,2)                                     | Valor                |
| fecha        | DATE                                              | Fecha del gasto      |
| metodo_pago  | ENUM('efectivo','tarjeta','transferencia','otro') |                      |
| nota         | TEXT                                              | Detalles adicionales |
| recurrente   | BOOLEAN DEFAULT FALSE                             |                      |
| id_categoria | INT FK → categorias(id_categoria)                 |                      |
| id_usuario   | INT FK → usuarios(id_usuario)                     | Usuario dueño        |
| id_grupo     | INT NULL FK → grupos(id_grupo)                    | Si pertenece a grupo |

---

### 6. **Ingresos**

Registra entradas de dinero personales o compartidas.

| Campo        | Tipo                              | Descripción                 |
| ------------ | --------------------------------- | --------------------------- |
| id_ingreso   | SERIAL PK                         | Identificador               |
| descripcion  | VARCHAR(255)                      | Detalle                     |
| monto        | DECIMAL(12,2)                     | Valor                       |
| fecha        | DATE                              | Fecha                       |
| fuente       | VARCHAR(100)                      | Ej: beca, trabajo, familiar |
| id_categoria | INT FK → categorias(id_categoria) |                             |
| id_usuario   | INT FK → usuarios(id_usuario)     |                             |
| id_grupo     | INT NULL FK → grupos(id_grupo)    | Opcional                    |

---

### 7. **Metas**

Metas financieras personales o compartidas.

| Campo           | Tipo                                    | Descripción                   |
| --------------- | --------------------------------------- | ----------------------------- |
| id_meta         | SERIAL PK                               | Identificador                 |
| nombre          | VARCHAR(100)                            | Ej: “Ahorro viaje fin de año” |
| monto_objetivo  | DECIMAL(12,2)                           | Meta                          |
| monto_acumulado | DECIMAL(12,2) DEFAULT 0                 | Ahorros actuales              |
| fecha_inicio    | DATE                                    |                               |
| fecha_fin       | DATE                                    |                               |
| estado          | ENUM('activa','completada','cancelada') |                               |
| id_usuario      | INT NULL FK → usuarios(id_usuario)      | Si es individual              |
| id_grupo        | INT NULL FK → grupos(id_grupo)          | Si es compartida              |

---

### 8. **Aportes_Metas**

Para registrar cuánto aporta cada usuario a una meta compartida.

| Campo      | Tipo                          | Descripción    |
| ---------- | ----------------------------- | -------------- |
| id_aporte  | SERIAL PK                     | Identificador  |
| id_meta    | INT FK → metas(id_meta)       |                |
| id_usuario | INT FK → usuarios(id_usuario) |                |
| monto      | DECIMAL(12,2)                 | Valor aportado |
| fecha      | DATE DEFAULT CURRENT_DATE     |                |

---

### 9. **Historial_AI (futuro para IA financiera)**

Registro de recomendaciones, análisis o evaluaciones.

| Campo        | Tipo                                      | Descripción    |
| ------------ | ----------------------------------------- | -------------- |
| id_historial | SERIAL PK                                 | Identificador  |
| id_usuario   | INT FK → usuarios(id_usuario)             |                |
| tipo         | ENUM('recomendacion','alerta','analisis') |                |
| contenido    | TEXT                                      | Texto generado |
| fecha        | TIMESTAMP DEFAULT NOW()                   | Fecha          |

---

## 🧠 EXPLICACIÓN FUNCIONAL

- **Usuarios**: entidad principal; cada usuario tiene ingresos, gastos, metas y puede pertenecer a varios grupos.
- **Categorías**: pueden ser **globales (visibles para todos)** o **personales** (ligadas a un usuario).
- **Grupos**: representan una unidad colaborativa (por ejemplo, "Casa de estudiantes", "Proyecto beca compartida").
- **Usuarios_Grupos**: define qué usuarios pertenecen a qué grupos y con qué rol.
- **Gastos e Ingresos**: pueden ser personales o de grupo, según si `id_grupo` es NULL o tiene valor.
- **Metas**: pueden ser personales (`id_usuario`) o grupales (`id_grupo`).
- **Aportes_Metas**: lleva control de cuánto aporta cada miembro a metas compartidas.
- **Historial_AI**: en el futuro servirá para registrar recomendaciones automáticas, predicciones o análisis financieros generados por IA.

---

¿Quieres que te cree ahora el **diagrama ERD visual actualizado** (con relaciones y claves foráneas) basado en este diseño?
Puedo entregártelo en formato imagen o código PlantUML para que lo exportes a Draw.io o MySQL Workbench.
