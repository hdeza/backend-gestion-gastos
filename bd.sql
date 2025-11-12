-- =====================================
-- TABLA USUARIOS
-- =====================================
CREATE TABLE usuarios (
  id_usuario SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(100) UNIQUE NOT NULL,
  contrasena_hash VARCHAR(255) NOT NULL,
  moneda_preferida VARCHAR(10),
  fecha_registro TIMESTAMP DEFAULT NOW(),
  foto_perfil VARCHAR(255),
  tipo_usuario VARCHAR(20) DEFAULT 'normal' CHECK (tipo_usuario IN ('normal', 'admin'))
);

-- =====================================
-- TABLA GRUPOS
-- =====================================
CREATE TABLE grupos (
  id_grupo SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  fecha_creacion TIMESTAMP DEFAULT NOW(),
  creado_por INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- =====================================
-- TABLA USUARIOS_GRUPOS
-- =====================================
CREATE TABLE usuarios_grupos (
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  id_grupo INT REFERENCES grupos(id_grupo) ON DELETE CASCADE,
  rol VARCHAR(20) DEFAULT 'miembro' CHECK (rol IN ('miembro','admin')),
  fecha_union TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (id_usuario, id_grupo)
);

-- =====================================
-- TABLA INVITACIONES
-- =====================================
CREATE TABLE invitaciones (
  id_invitacion SERIAL PRIMARY KEY,
  id_grupo INT REFERENCES grupos(id_grupo) ON DELETE CASCADE NOT NULL,
  token VARCHAR(64) UNIQUE NOT NULL,
  creado_por INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE NOT NULL,
  id_usuario_invitado INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente','aceptada','rechazada','expirada')),
  fecha_creacion TIMESTAMP DEFAULT NOW(),
  fecha_expiracion TIMESTAMP,
  fecha_aceptacion TIMESTAMP,
  usado BOOLEAN DEFAULT FALSE
);

-- Índice para búsqueda rápida por token
CREATE INDEX idx_invitaciones_token ON invitaciones(token);

-- =====================================
-- TABLA CATEGORIAS
-- =====================================
CREATE TABLE categorias (
  id_categoria SERIAL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  tipo VARCHAR(20) CHECK (tipo IN ('ingreso','gasto')),
  color VARCHAR(20),
  icono VARCHAR(100),
  es_global BOOLEAN DEFAULT FALSE,
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- =====================================
-- TABLA GASTOS
-- =====================================
CREATE TABLE gastos (
  id_gasto SERIAL PRIMARY KEY,
  descripcion VARCHAR(255) NOT NULL,
  monto DECIMAL(12,2) NOT NULL CHECK (monto >= 0),
  fecha DATE NOT NULL,
  metodo_pago VARCHAR(30) CHECK (metodo_pago IN ('efectivo','tarjeta','transferencia','otro')),
  nota TEXT,
  recurrente BOOLEAN DEFAULT FALSE,
  id_categoria INT REFERENCES categorias(id_categoria) ON DELETE SET NULL,
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  id_grupo INT REFERENCES grupos(id_grupo) ON DELETE CASCADE
);

-- =====================================
-- TABLA INGRESOS
-- =====================================
CREATE TABLE ingresos (
  id_ingreso SERIAL PRIMARY KEY,
  descripcion VARCHAR(255) NOT NULL,
  monto DECIMAL(12,2) NOT NULL CHECK (monto >= 0),
  fecha DATE NOT NULL,
  fuente VARCHAR(100),
  id_categoria INT REFERENCES categorias(id_categoria) ON DELETE SET NULL,
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  id_grupo INT REFERENCES grupos(id_grupo) ON DELETE CASCADE
);

-- =====================================
-- TABLA METAS
-- =====================================
CREATE TABLE metas (
  id_meta SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  monto_objetivo DECIMAL(12,2) NOT NULL,
  monto_acumulado DECIMAL(12,2) DEFAULT 0,
  fecha_inicio DATE,
  fecha_fin DATE,
  estado VARCHAR(20) CHECK (estado IN ('activa','completada','cancelada')),
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  id_grupo INT REFERENCES grupos(id_grupo) ON DELETE CASCADE
);

-- =====================================
-- TABLA APORTES_METAS
-- =====================================
CREATE TABLE aportes_metas (
  id_aporte SERIAL PRIMARY KEY,
  id_meta INT REFERENCES metas(id_meta) ON DELETE CASCADE,
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  monto DECIMAL(12,2) NOT NULL CHECK (monto >= 0),
  fecha DATE DEFAULT CURRENT_DATE
);

-- =====================================
-- TABLA HISTORIAL_AI
-- =====================================
CREATE TABLE historial_ai (
  id_historial SERIAL PRIMARY KEY,
  id_usuario INT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
  tipo VARCHAR(20) CHECK (tipo IN ('recomendacion','alerta','analisis')),
  contenido TEXT NOT NULL,
  fecha TIMESTAMP DEFAULT NOW()
);

-- =====================================
-- DATOS INICIALES - CATEGORÍAS GLOBALES
-- =====================================

-- Categorías de Gastos Globales
INSERT INTO categorias (nombre, tipo, color, icono, es_global) VALUES
('Alimentación', 'gasto', '#FF6B6B', '🍽️', TRUE),
('Transporte', 'gasto', '#4ECDC4', '🚌', TRUE),
('Educación', 'gasto', '#45B7D1', '📚', TRUE),
('Entretenimiento', 'gasto', '#96CEB4', '🎬', TRUE),
('Salud', 'gasto', '#FFEAA7', '🏥', TRUE),
('Ropa y Accesorios', 'gasto', '#DDA0DD', '👕', TRUE),
('Servicios Básicos', 'gasto', '#98D8C8', '💡', TRUE),
('Tecnología', 'gasto', '#A8E6CF', '💻', TRUE),
('Deportes', 'gasto', '#FFD93D', '⚽', TRUE),
('Viajes', 'gasto', '#6C5CE7', '✈️', TRUE),
('Regalos', 'gasto', '#FD79A8', '🎁', TRUE),
('Hogar', 'gasto', '#E17055', '🏠', TRUE),
('Belleza', 'gasto', '#FDCB6E', '💄', TRUE),
('Suscripciones', 'gasto', '#E84393', '📱', TRUE),
('Otros Gastos', 'gasto', '#636E72', '💰', TRUE);

-- Categorías de Ingresos Globales
INSERT INTO categorias (nombre, tipo, color, icono, es_global) VALUES
('Salario', 'ingreso', '#00B894', '💼', TRUE),
('Becas', 'ingreso', '#00CEC9', '🎓', TRUE),
('Trabajo Freelance', 'ingreso', '#0984E3', '💻', TRUE),
('Regalos', 'ingreso', '#E84393', '🎁', TRUE),
('Préstamos', 'ingreso', '#FDCB6E', '💰', TRUE),
('Reembolsos', 'ingreso', '#6C5CE7', '🔄', TRUE),
('Dividendos', 'ingreso', '#A29BFE', '📈', TRUE),
('Venta de Artículos', 'ingreso', '#FD79A8', '🏷️', TRUE),
('Trabajo de Verano', 'ingreso', '#00B894', '☀️', TRUE),
('Ayuda Familiar', 'ingreso', '#FDCB6E', '👨‍👩‍👧‍👦', TRUE),
('Premios', 'ingreso', '#FFD93D', '🏆', TRUE),
('Otros Ingresos', 'ingreso', '#636E72', '💵', TRUE);
