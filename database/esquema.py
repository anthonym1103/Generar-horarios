"""Definición del esquema SQLite del generador de horarios.

Convenciones:
- 1 "hora" = 1 hora académica = 1 período = 1 fila de la tabla `bloque`.
- Un "bloque de 2 horas" es una asignatura con bloques_consecutivos = 2.
"""

ESQUEMA_SQL = """
-- Turnos del liceo (mañana, tarde). El rango es editable por el usuario.
CREATE TABLE IF NOT EXISTS turno (
    id                INTEGER PRIMARY KEY,
    nombre            TEXT NOT NULL UNIQUE,   -- 'Mañana', 'Tarde'
    hora_inicio       TEXT NOT NULL,          -- 'HH:MM'
    hora_fin          TEXT NOT NULL,          -- 'HH:MM'
    num_periodos      INTEGER NOT NULL CHECK (num_periodos > 0),
    duracion_periodo  INTEGER NOT NULL CHECK (duracion_periodo > 0)   -- minutos
);

-- Recreo del turno: uno solo por turno. Duración y después de qué período ocurre.
CREATE TABLE IF NOT EXISTS recreo (
    id                 INTEGER PRIMARY KEY,
    turno_id           INTEGER NOT NULL UNIQUE REFERENCES turno(id) ON DELETE CASCADE,
    despues_de_periodo INTEGER NOT NULL CHECK (despues_de_periodo >= 1),
    duracion           INTEGER NOT NULL CHECK (duracion > 0)          -- minutos
);

CREATE TABLE IF NOT EXISTS anio (
    id      INTEGER PRIMARY KEY,
    nombre  TEXT NOT NULL UNIQUE       -- '1er año', '2do año', ...
);

-- Turnos en los que un año ve clases: mañana = 1 fila, tarde = 1 fila,
-- turno completo = 2 filas
CREATE TABLE IF NOT EXISTS anio_turno (
    id        INTEGER PRIMARY KEY,
    anio_id   INTEGER NOT NULL REFERENCES anio(id)  ON DELETE CASCADE,
    turno_id  INTEGER NOT NULL REFERENCES turno(id) ON DELETE RESTRICT,
    UNIQUE (anio_id, turno_id)
);

CREATE TABLE IF NOT EXISTS seccion (
    id      INTEGER PRIMARY KEY,
    letra   TEXT NOT NULL UNIQUE CHECK (length(letra) = 1)   -- 'A', 'B', ...
);

-- Combinación concreta año + sección (ej: 3er año "A")
CREATE TABLE IF NOT EXISTS anio_curso (
    id          INTEGER PRIMARY KEY,
    anio_id     INTEGER NOT NULL REFERENCES anio(id)    ON DELETE CASCADE,
    seccion_id  INTEGER NOT NULL REFERENCES seccion(id) ON DELETE CASCADE,
    UNIQUE (anio_id, seccion_id)
);

-- EXCEPCIONES: turno propio de una sección distinto al de su año.
-- Si una sección tiene filas aquí, estas reemplazan a las de anio_turno.
CREATE TABLE IF NOT EXISTS anio_curso_turno (
    id             INTEGER PRIMARY KEY,
    anio_curso_id  INTEGER NOT NULL REFERENCES anio_curso(id) ON DELETE CASCADE,
    turno_id       INTEGER NOT NULL REFERENCES turno(id)      ON DELETE RESTRICT,
    UNIQUE (anio_curso_id, turno_id)
);

-- Turnos efectivos de cada sección: su excepción si existe, si no los de su año.
CREATE VIEW IF NOT EXISTS v_seccion_turno AS
SELECT act.anio_curso_id, act.turno_id
FROM anio_curso_turno act
UNION ALL
SELECT ac.id, atu.turno_id
FROM anio_curso ac
JOIN anio_turno atu ON atu.anio_id = ac.anio_id
WHERE NOT EXISTS (SELECT 1 FROM anio_curso_turno x WHERE x.anio_curso_id = ac.id);

-- Catálogo de materias por nivel (sin sección).
-- Los bloques semanales son los del pénsum: valen para todas las secciones del año.
CREATE TABLE IF NOT EXISTS asignatura (
    id                    INTEGER PRIMARY KEY,
    anio_id               INTEGER NOT NULL REFERENCES anio(id) ON DELETE CASCADE,
    nombre                TEXT NOT NULL,
    bloques_semanales     INTEGER NOT NULL CHECK (bloques_semanales > 0),
    -- por defecto cada sesión son 2 períodos seguidos (= 2 horas)
    bloques_consecutivos  INTEGER NOT NULL DEFAULT 2 CHECK (bloques_consecutivos >= 1),
    UNIQUE (anio_id, nombre),
    -- los bloques semanales deben poder agruparse en sesiones completas
    CHECK (bloques_semanales % bloques_consecutivos = 0)
);

CREATE TABLE IF NOT EXISTS profesor (
    id               INTEGER PRIMARY KEY,
    nombre           TEXT NOT NULL,
    apellido         TEXT NOT NULL,
    horas_semanales  INTEGER NOT NULL CHECK (horas_semanales > 0)   -- ej: 48
);

-- Turnos en los que trabaja el profesor: solo mañana = 1 fila, turno completo = 2 filas
CREATE TABLE IF NOT EXISTS profesor_turno (
    id           INTEGER PRIMARY KEY,
    profesor_id  INTEGER NOT NULL REFERENCES profesor(id) ON DELETE CASCADE,
    turno_id     INTEGER NOT NULL REFERENCES turno(id)    ON DELETE CASCADE,
    UNIQUE (profesor_id, turno_id)
);

-- Relación muchos a muchos: qué asignaturas (cada una ya ligada a un año)
-- puede dictar cada profesor
CREATE TABLE IF NOT EXISTS profesor_asignatura (
    id             INTEGER PRIMARY KEY,
    profesor_id    INTEGER NOT NULL REFERENCES profesor(id)   ON DELETE CASCADE,
    asignatura_id  INTEGER NOT NULL REFERENCES asignatura(id) ON DELETE CASCADE,
    UNIQUE (profesor_id, asignatura_id)
);

-- 'activo' = el liceo da clases ese día (por defecto lunes a viernes)
CREATE TABLE IF NOT EXISTS dia (
    id      INTEGER PRIMARY KEY,
    nombre  TEXT NOT NULL UNIQUE,
    activo  INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

-- Cada bloque (período) pertenece a un turno.
-- 'orden' es la posición dentro del turno (1, 2, 3...).
CREATE TABLE IF NOT EXISTS bloque (
    id           INTEGER PRIMARY KEY,
    turno_id     INTEGER NOT NULL REFERENCES turno(id) ON DELETE CASCADE,
    orden        INTEGER NOT NULL,
    hora_inicio  TEXT NOT NULL,   -- 'HH:MM'
    hora_fin     TEXT NOT NULL,   -- 'HH:MM'
    UNIQUE (turno_id, orden)
);

-- Qué necesita cada sección: materia y cuántos bloques a la semana.
-- profesor_id es NULL hasta que el generador (o el usuario) asigna un profesor.
CREATE TABLE IF NOT EXISTS carga_academica (
    id                    INTEGER PRIMARY KEY,
    anio_curso_id         INTEGER NOT NULL REFERENCES anio_curso(id) ON DELETE CASCADE,
    asignatura_id         INTEGER NOT NULL REFERENCES asignatura(id) ON DELETE CASCADE,
    profesor_id           INTEGER,
    -- 1 = el usuario fijó este profesor y el generador debe respetarlo
    profesor_fijo         INTEGER NOT NULL DEFAULT 0 CHECK (profesor_fijo IN (0, 1)),
    bloques_semanales     INTEGER NOT NULL CHECK (bloques_semanales > 0),
    bloques_consecutivos  INTEGER NOT NULL DEFAULT 2 CHECK (bloques_consecutivos >= 1),
    UNIQUE (anio_curso_id, asignatura_id),
    CHECK (bloques_semanales % bloques_consecutivos = 0),
    -- el profesor asignado debe dictar esa asignatura (no se valida si es NULL)
    FOREIGN KEY (profesor_id, asignatura_id)
        REFERENCES profesor_asignatura(profesor_id, asignatura_id)
);

-- Resultado del generador
CREATE TABLE IF NOT EXISTS horario (
    id             INTEGER PRIMARY KEY,
    anio_curso_id  INTEGER NOT NULL REFERENCES anio_curso(id) ON DELETE CASCADE,
    dia_id         INTEGER NOT NULL REFERENCES dia(id),
    bloque_id      INTEGER NOT NULL REFERENCES bloque(id),
    asignatura_id  INTEGER NOT NULL REFERENCES asignatura(id) ON DELETE CASCADE,
    profesor_id    INTEGER NOT NULL REFERENCES profesor(id)   ON DELETE RESTRICT,
    -- una sección no puede tener dos clases a la misma hora
    UNIQUE (anio_curso_id, dia_id, bloque_id),
    -- un profesor no puede estar en dos secciones a la misma hora
    UNIQUE (profesor_id, dia_id, bloque_id)
);

CREATE INDEX IF NOT EXISTS idx_horario_seccion ON horario(anio_curso_id);
CREATE INDEX IF NOT EXISTS idx_carga_seccion   ON carga_academica(anio_curso_id);

-- Capacidad máxima de horas por semana de cada profesor según sus turnos:
-- (bloques de cada turno que trabaja) x (días activos).
-- Ej: solo mañana con 7 bloques x 5 días = 35.
CREATE VIEW IF NOT EXISTS v_profesor_capacidad AS
SELECT
    p.id AS profesor_id,
    p.nombre,
    p.apellido,
    p.horas_semanales,
    COALESCE((
        SELECT COUNT(*)
        FROM profesor_turno pt
        JOIN bloque b ON b.turno_id = pt.turno_id
        WHERE pt.profesor_id = p.id
    ), 0) * (SELECT COUNT(*) FROM dia WHERE activo = 1) AS capacidad_maxima
FROM profesor p;

-- ---------------------------------------------------------------------------
-- Reglas que la base hace cumplir
-- ---------------------------------------------------------------------------

-- Un horario solo puede usar bloques del turno del año de esa sección,
-- y el profesor debe trabajar en ese turno.
CREATE TRIGGER IF NOT EXISTS trg_horario_turno
BEFORE INSERT ON horario
BEGIN
    SELECT RAISE(ABORT, 'El bloque no pertenece a un turno de la sección')
    WHERE NOT EXISTS (
        SELECT 1 FROM bloque b
        JOIN v_seccion_turno st ON st.turno_id = b.turno_id
        WHERE b.id = NEW.bloque_id AND st.anio_curso_id = NEW.anio_curso_id
    );

    SELECT RAISE(ABORT, 'El profesor no trabaja en el turno de ese bloque')
    WHERE NOT EXISTS (
        SELECT 1 FROM profesor_turno pt
        JOIN bloque b ON b.turno_id = pt.turno_id
        WHERE pt.profesor_id = NEW.profesor_id AND b.id = NEW.bloque_id
    );
END;

-- Al asignar un profesor a una carga: debe trabajar en el turno del año
-- y no puede pasarse de sus horas semanales.
CREATE TRIGGER IF NOT EXISTS trg_carga_profesor_ins
BEFORE INSERT ON carga_academica
WHEN NEW.profesor_id IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'El profesor no trabaja en el turno de esa sección')
    WHERE NOT EXISTS (
        SELECT 1 FROM profesor_turno pt
        JOIN v_seccion_turno st ON st.turno_id = pt.turno_id
        WHERE pt.profesor_id = NEW.profesor_id AND st.anio_curso_id = NEW.anio_curso_id
    );

    SELECT RAISE(ABORT, 'El profesor excede sus horas semanales')
    WHERE (SELECT COALESCE(SUM(bloques_semanales), 0) FROM carga_academica
           WHERE profesor_id = NEW.profesor_id AND id IS NOT NEW.id)
          + NEW.bloques_semanales
          > (SELECT horas_semanales FROM profesor WHERE id = NEW.profesor_id);
END;

CREATE TRIGGER IF NOT EXISTS trg_carga_profesor_upd
BEFORE UPDATE OF profesor_id, bloques_semanales ON carga_academica
WHEN NEW.profesor_id IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'El profesor no trabaja en el turno de esa sección')
    WHERE NOT EXISTS (
        SELECT 1 FROM profesor_turno pt
        JOIN v_seccion_turno st ON st.turno_id = pt.turno_id
        WHERE pt.profesor_id = NEW.profesor_id AND st.anio_curso_id = NEW.anio_curso_id
    );

    SELECT RAISE(ABORT, 'El profesor excede sus horas semanales')
    WHERE (SELECT COALESCE(SUM(bloques_semanales), 0) FROM carga_academica
           WHERE profesor_id = NEW.profesor_id AND id IS NOT NEW.id)
          + NEW.bloques_semanales
          > (SELECT horas_semanales FROM profesor WHERE id = NEW.profesor_id);
END;
"""

# Días que siempre deben existir: (nombre, activo)
DIAS_INICIALES = [
    ("Lunes", 1),
    ("Martes", 1),
    ("Miércoles", 1),
    ("Jueves", 1),
    ("Viernes", 1),
    ("Sábado", 0),
]