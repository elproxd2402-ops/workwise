-- Datos ficticios SOLO para probar la interfaz local. No representan empresas reales.
TRUNCATE TABLE ofertas, sanciones_sunafil, resenas, empresas RESTART IDENTITY CASCADE;

INSERT INTO empresas (nombre, sector, ciudad, exige_titulo, apto_joven, resumen_ia, latitud, longitud, web_aplicacion, es_demo)
VALUES
('Comercio Andino Demo', 'Retail', 'Lima', FALSE, TRUE, 'Buen ambiente según varias reseñas. Algunas personas mencionan días con bastante carga de trabajo.', -12.0464, -77.0428, 'https://example.com/postular/andino', TRUE),
('Servicios Costa Demo', 'Servicios', 'Lima', FALSE, TRUE, 'Se valoran los equipos amables y el aprendizaje. Hay quejas sobre horarios que pueden cambiar con poca anticipación.', -12.1187, -77.0285, 'https://example.com/postular/costa', TRUE),
('Tecnología Norte Demo', 'Tecnología', 'Trujillo', TRUE, FALSE, 'Las reseñas hablan de buenos proyectos, pero el puesto de ejemplo pide título y no es apto para menores de edad.', -8.1116, -79.0287, 'https://example.com/postular/tecnologia', TRUE);

INSERT INTO resenas (empresa_id, texto, rating, fecha, fuente)
VALUES
(1, 'El equipo me ayudó a aprender bastante. El trabajo es movido, pero los compañeros son buena onda.', 5, '2026-07-10', 'DEMO'),
(1, 'Hay días pesados y toca atender bastante público. El pago fue puntual.', 4, '2026-06-18', 'DEMO'),
(1, 'Me gustó que me explicaran el trabajo desde cero.', 5, '2026-05-03', 'DEMO'),
(2, 'Buen trato de mi jefe y compañeros. Aprendí rápido.', 4, '2026-07-22', 'DEMO'),
(2, 'Los turnos a veces cambian y eso puede complicar organizarse.', 3, '2026-06-01', 'DEMO'),
(2, 'El ambiente fue tranquilo cuando había suficiente personal.', 4, '2026-04-14', 'DEMO'),
(3, 'Buen aprendizaje técnico, pero el proceso fue más exigente de lo que esperaba.', 4, '2026-06-12', 'DEMO');

INSERT INTO sanciones_sunafil (empresa_id, tipo, fecha, fuente)
VALUES
(2, 'Incumplimiento laboral (dato ficticio de demostración)', '2026-02-20', 'DEMO');

INSERT INTO ofertas (empresa_id, titulo_puesto, descripcion, requiere_titulo, jornada_horas, apto_joven, alertas, url_aplicacion)
VALUES
(1, 'Auxiliar de tienda', 'Atender clientes, ordenar productos y apoyar en caja.', FALSE, 6, TRUE, 'Evita turnos nocturnos si tienes 17 años.', 'https://example.com/postular/andino/auxiliar'),
(1, 'Asistente de almacén', 'Ordenar mercadería y apoyar inventarios.', FALSE, 5, TRUE, NULL, 'https://example.com/postular/andino/almacen'),
(2, 'Atención al cliente', 'Resolver dudas y registrar pedidos.', FALSE, 6, TRUE, 'Revisa bien el turno antes de aceptar.', 'https://example.com/postular/costa/atencion'),
(2, 'Auxiliar operativo', 'Apoyo general en las tareas diarias.', FALSE, 8, FALSE, 'Una jornada de 8 horas no es apta para un trabajador de 17 años.', 'https://example.com/postular/costa/operativo'),
(3, 'Practicante técnico', 'Apoyo en proyectos de software.', TRUE, 6, FALSE, 'Requiere título según el ejemplo de datos.', 'https://example.com/postular/tecnologia/practicante');

UPDATE empresas e
SET
    puntaje = ROUND(
        (
            COALESCE(
                (
                    SELECT AVG(r.rating)
                    FROM resenas r
                    WHERE r.empresa_id = e.id
                ),
                0
            ) * 8
        )
        +
        GREATEST(
            0,
            30 - (
                10 * COALESCE(
                    (
                        SELECT COUNT(*)
                        FROM sanciones_sunafil s
                        WHERE s.empresa_id = e.id
                    ),
                    0
                )
            )
        )
        +
        CASE
            WHEN e.apto_joven THEN 20
            ELSE 0
        END
        +
        CASE
            WHEN NOT e.exige_titulo THEN 10
            ELSE 0
        END,
        1
    ),

    semaforo = CASE
        WHEN (
            (
                COALESCE(
                    (
                        SELECT AVG(r.rating)
                        FROM resenas r
                        WHERE r.empresa_id = e.id
                    ),
                    0
                ) * 8
            )
            +
            GREATEST(
                0,
                30 - (
                    10 * COALESCE(
                        (
                            SELECT COUNT(*)
                            FROM sanciones_sunafil s
                            WHERE s.empresa_id = e.id
                        ),
                        0
                    )
                )
            )
            +
            CASE
                WHEN e.apto_joven THEN 20
                ELSE 0
            END
            +
            CASE
                WHEN NOT e.exige_titulo THEN 10
                ELSE 0
            END
        ) >= 70 THEN 'verde'

        WHEN (
            (
                COALESCE(
                    (
                        SELECT AVG(r.rating)
                        FROM resenas r
                        WHERE r.empresa_id = e.id
                    ),
                    0
                ) * 8
            )
            +
            GREATEST(
                0,
                30 - (
                    10 * COALESCE(
                        (
                            SELECT COUNT(*)
                            FROM sanciones_sunafil s
                            WHERE s.empresa_id = e.id
                        ),
                        0
                    )
                )
            )
            +
            CASE
                WHEN e.apto_joven THEN 20
                ELSE 0
            END
            +
            CASE
                WHEN NOT e.exige_titulo THEN 10
                ELSE 0
            END
        ) >= 40 THEN 'amarillo'

        ELSE 'rojo'
    END;