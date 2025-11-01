-- =====================================
-- SCRIPT PARA INSERTAR CATEGORÍAS GLOBALES
-- Ejecutar solo si ya tienes las tablas creadas
-- =====================================

-- Verificar si ya existen categorías globales para evitar duplicados
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM categorias WHERE es_global = TRUE LIMIT 1) THEN
        
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

        RAISE NOTICE '✅ Categorías globales insertadas exitosamente';

    ELSE
        RAISE NOTICE '⚠️ Las categorías globales ya existen, no se insertaron duplicados';
    END IF;
END $$;
