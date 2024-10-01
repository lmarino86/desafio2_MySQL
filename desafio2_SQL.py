import mysql.connector
from mysql.connector import Error
from decimal import Decimal

class CuentaBancaria:
    def __init__(self, numero_cuenta, saldo, titular):
        self.__numero_cuenta = numero_cuenta
        self.__saldo = saldo
        self.__titular = titular

    def depositar(self, monto):
        # Realiza un depósito en la cuenta.
        if monto > 0:
            self.__saldo += monto
        else:
            raise ValueError("El monto de depósito debe ser positivo.")

    def retirar(self, monto):
        # Realiza un retiro de la cuenta.
        if 0 < monto <= self.__saldo:
            self.__saldo -= monto
        else:
            raise ValueError("Monto de retiro inválido o saldo insuficiente.")

    def obtener_info(self):
        # Devuelve la información de la cuenta.
        return {
            "numero_cuenta": self.__numero_cuenta,
            "saldo": float(self.__saldo),
            "titular": self.__titular
        }

    def to_dict(self):
        return self.obtener_info()

class CuentaBancariaCorriente(CuentaBancaria):
    def __init__(self, numero_cuenta, saldo, titular, descubierto):
        super().__init__(numero_cuenta, saldo, titular)
        self.__descubierto = descubierto

    def retirar(self, monto):
        # Realiza un retiro considerando el descubierto.
        if 0 < monto <= self._CuentaBancaria__saldo + self.__descubierto:
            self._CuentaBancaria__saldo -= monto
        else:
            raise ValueError("Monto de retiro inválido o saldo insuficiente.")

    def obtener_info(self):
        info = super().obtener_info()
        info["descubierto"] = float(self.__descubierto)
        return info

class CuentaBancariaAhorro(CuentaBancaria):
    def __init__(self, numero_cuenta, saldo, titular, tasa_interes):
        super().__init__(numero_cuenta, saldo, titular)
        self.__tasa_interes = tasa_interes

    def aplicar_interes(self):
        # Aplica la tasa de interés al saldo.
        self._CuentaBancaria__saldo += self._CuentaBancaria__saldo * (self.__tasa_interes / 100)

    def obtener_info(self):
        info = super().obtener_info()
        info["tasa_interes"] = float(self.__tasa_interes)
        return info

class GestionCuentas:
    def __init__(self, db_config):
        self.connection = self.create_connection(db_config)
        self.create_table()

    def create_connection(self, db_config):
        # Crea la conexión a la base de datos.
        connection = None
        try:
            connection = mysql.connector.connect(**db_config)
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
        return connection

    def create_table(self):
        # Crea la tabla de cuentas si no existe.
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cuentas (
            numero_cuenta VARCHAR(255) PRIMARY KEY,
            saldo DECIMAL(10, 2) NOT NULL,
            titular VARCHAR(255) NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            descubierto DECIMAL(10, 2),
            tasa_interes DECIMAL(5, 2)
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(create_table_query)
        self.connection.commit()

    def agregar_cuenta(self, cuenta):
        # Agrega una nueva cuenta a la base de datos.
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO cuentas (numero_cuenta, saldo, titular, tipo, descubierto, tasa_interes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                cuenta.obtener_info()["numero_cuenta"],
                cuenta.obtener_info()["saldo"],
                cuenta.obtener_info()["titular"],
                cuenta.__class__.__name__,
                getattr(cuenta, '_CuentaBancariaCorriente__descubierto', None),
                getattr(cuenta, '_CuentaBancariaAhorro__tasa_interes', None)
            ))
            self.connection.commit()
        except mysql.connector.IntegrityError:
            raise ValueError("El número de cuenta debe ser único.")
        except Error as e:
            print(f"Error al agregar la cuenta: {e}")

    def eliminar_cuenta(self, numero_cuenta):
        # Elimina una cuenta de la base de datos.
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM cuentas WHERE numero_cuenta = %s"
            cursor.execute(delete_query, (numero_cuenta,))
            self.connection.commit()
        except Error as e:
            print(f"Error al eliminar la cuenta: {e}")
    
    def obtener_cuenta(self, numero_cuenta):
        # Obtiene una cuenta de la base de datos.
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM cuentas WHERE numero_cuenta = %s"
        cursor.execute(query, (numero_cuenta,))
        cuenta = cursor.fetchone()
        
        # Convertir campos de Decimal a float
        if cuenta:
            cuenta['saldo'] = float(cuenta['saldo'])
            cuenta['descubierto'] = float(cuenta['descubierto']) if cuenta['descubierto'] is not None else None
            cuenta['tasa_interes'] = float(cuenta['tasa_interes']) if cuenta['tasa_interes'] is not None else None
        
        return cuenta


    def actualizar_cuenta(self, numero_cuenta, saldo=None, titular=None):
        # Actualiza la información de una cuenta.
        try:
            cursor = self.connection.cursor()
            update_fields = []
            update_values = []
            if saldo is not None:
                update_fields.append("saldo = %s")
                update_values.append(saldo)
            if titular is not None:
                update_fields.append("titular = %s")
                update_values.append(titular)
            update_values.append(numero_cuenta)

            update_query = f"UPDATE cuentas SET {', '.join(update_fields)} WHERE numero_cuenta = %s"
            cursor.execute(update_query, update_values)
            self.connection.commit()
        except Error as e:
            print(f"Error al actualizar la cuenta: {e}")

