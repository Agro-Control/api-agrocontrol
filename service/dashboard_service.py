from connection.postgres import Database
from errors import DatabaseError


class DashBoardsService:

    def dash_operadores_operantes_por_totais(self, grupo_id: int = None, empresa_id: int = None, unidade_id:int = None):
        dash = {}

        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                params = []

                sql_sub = """
                    SELECT 
                        COUNT(*)
                    FROM usuario u
                    INNER JOIN unidade un ON u.unidade_id  = un.id 
                    INNER JOIN empresa e ON e.id = un.empresa_id 
                    WHERE u.tipo = 'O'
                """

                if grupo_id:
                    sql_sub += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                elif empresa_id:
                    sql_sub += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql_sub += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                sql = f"""
                    SELECT 
                        COUNT(*) AS operadores_ativos,
                        ({sql_sub}) operadores_totais
                    FROM usuario u
                    LEFT JOIN ordem_servico_operador oso ON oso.operador_id = u.id
                    LEFT JOIN ordem_servico os ON os.id = oso.ordem_servico_id
                    INNER JOIN unidade un ON u.unidade_id  = un.id 
                    INNER JOIN empresa e ON  e.id = un.empresa_id 
                    WHERE os.status = 'E' 
                    AND u.tipo = 'O'
                """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.unidade_id = %s"
                    params.append(unidade_id)

                cursor.execute(sql, params, prepare=True)

                result = cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    def dash_maquinas_operantes_por_totais(self,grupo_id:int = None,
                                           unidade_id: int = None,
                                           empresa_id: int = None):
        dash = {}

        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                params = []

                sql_sub = """
                            SELECT 
                                COUNT(*)
                            FROM maquina m
                            INNER JOIN unidade u ON m.unidade_id  = u.id
                            INNER JOIN empresa e ON u.empresa_id = e.id
                            WHERE m.status = 'A'
                        """

                if grupo_id:
                    sql_sub += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql_sub += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql_sub += " AND m.unidade_id = %s"
                    params.append(unidade_id)

                sql = f"""
                        SELECT 
                            COUNT(*) AS maquina_operando,
                            ({sql_sub}) maquinas_total
                        FROM maquina m
                        LEFT JOIN ordem_servico os ON os.maquina_id = m.id
                        INNER JOIN unidade u ON m.unidade_id  = u.id
                        INNER JOIN empresa e ON u.empresa_id = e.id
                        WHERE m.status = 'A'
                        AND os.status in ('A', 'E')
                """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND m.unidade_id = %s"
                    params.append(unidade_id)

                cursor.execute(sql, params, prepare=True)

                result = cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    def dash_ordem_ativas(self, grupo_id:int = None,
                               unidade_id: int = None,
                               empresa_id: int = None):

        dash = {}

        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:

                params = []

                sql = """
                        SELECT 
                            count(*) ordens_ativas
                        FROM ordem_servico os
                        INNER JOIN unidade u ON os.unidade_id = u.id 
                        INNER JOIN empresa e ON e.id  = os.empresa_id 
                        WHERE os.status in ('A', 'E')

                    """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND U.ID = %s"
                    params.append(unidade_id)

                cursor.execute(sql, params, prepare=True)

                result = cursor.fetchone()

                if not result:
                    return {}

                dash = result

        return dash


    def dash_ordem_status(self,
                          grupo_id: int = None,
                          unidade_id: int = None,
                          empresa_id: int = None
                          ):

        dash = {}

        with Database() as conn:
            with conn.cursor(row_factory=Database.get_cursor_type("dict")) as cursor:
                params_total = []
                params = []

                sql_total = """
                    select 
                        COUNT(os.*) total 
                    from ordem_servico os
                    inner join empresa e ON e.id  = os.empresa_id 
                    join unidade u ON os.unidade_id = u.id 
                    WHERE 1=1
                """

                if grupo_id:
                    sql_total += " AND e.grupo_id = %s"
                    params_total.append(grupo_id)

                if empresa_id:
                    sql_total += " AND e.id = %s"
                    params_total.append(empresa_id)

                if unidade_id:
                    sql_total += " AND u.id = %s"
                    params_total.append(unidade_id)

                cursor.execute(sql_total, params_total, prepare=True)

                result = cursor.fetchone()

                if not result:
                    dash['total_de_ordens'] = 0
                    return dash

                dash['total_de_ordens'] = result['total']

                sql = """
                    SELECT 
                        CASE
                            WHEN os.status = 'A' THEN 'Ativa'
                            WHEN os.status = 'E' THEN 'Em andamento'
                            WHEN os.status = 'F' THEN 'Finalizado'
                            WHEN os.status = 'C' THEN 'Cancelado'
                        ELSE
                            'Fez merda'
                        END as "STATUS",
                        COUNT(os.id) total
                    FROM ordem_servico os
                    INNER JOIN unidade u ON os.unidade_id = u.id 
                    INNER JOIN empresa e ON e.id  = os.empresa_id 
                    WHERE 1 = 1
                """

                if grupo_id:
                    sql += " AND e.grupo_id = %s"
                    params.append(grupo_id)

                if empresa_id:
                    sql += " AND e.id = %s"
                    params.append(empresa_id)

                if unidade_id:
                    sql += " AND u.id = %s"
                    params.append(unidade_id)

                sql += " GROUP BY os.status"

                cursor.execute(sql, params, prepare=True)

                result = cursor.fetchall()

                if not result:
                    return dash

                for row in result:
                    dash[row['STATUS']] = row['total']

        return dash

