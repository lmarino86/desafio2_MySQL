from desafio2_SQL import CuentaBancaria, CuentaBancariaCorriente, CuentaBancariaAhorro, GestionCuentas
import json

def mostrar_menu():
    print("1. Agregar cuenta")
    print("2. Eliminar cuenta")
    print("3. Actualizar cuenta")
    print("4. Ver información de cuenta")
    print("5. Salir")

def main():
    db_config = {
        'host': 'localhost',
        'user': 'usuario',
        'password': 'contraseña',
        'database': 'base de datos'
    }
    
    gestion = GestionCuentas(db_config)
    
    while True:
        mostrar_menu()
        try:
            opcion = int(input("Seleccione una opción: "))
            if opcion == 1:
                numero_cuenta = input("Número de cuenta: ")
                saldo = float(input("Saldo inicial: "))
                titular = input("Titular de la cuenta: ")
                tipo = input("Tipo de cuenta (corriente/ahorro): ").lower()
                
                if tipo == 'corriente':
                    descubierto = float(input("Límite de descubierto: "))
                    cuenta = CuentaBancariaCorriente(numero_cuenta, saldo, titular, descubierto)
                elif tipo == 'ahorro':
                    tasa_interes = float(input("Tasa de interés: "))
                    cuenta = CuentaBancariaAhorro(numero_cuenta, saldo, titular, tasa_interes)
                else:
                    cuenta = CuentaBancaria(numero_cuenta, saldo, titular)
                
                gestion.agregar_cuenta(cuenta)
                print("Cuenta agregada exitosamente.")
                
            elif opcion == 2:
                numero_cuenta = input("Número de cuenta a eliminar: ")
                gestion.eliminar_cuenta(numero_cuenta)
                print("Cuenta eliminada exitosamente.")
                
            elif opcion == 3:
                numero_cuenta = input("Número de cuenta a actualizar: ")
                saldo = input("Nuevo saldo (deje en blanco para no cambiar): ")
                titular = input("Nuevo titular (deje en blanco para no cambiar): ")
                saldo = float(saldo) if saldo else None
                gestion.actualizar_cuenta(numero_cuenta, saldo, titular)
                print("Cuenta actualizada exitosamente.")
                
            elif opcion == 4:
                numero_cuenta = input("Número de cuenta a consultar: ")
                cuenta = gestion.obtener_cuenta(numero_cuenta)
                if cuenta:
                    print(json.dumps(cuenta, indent=4))
                else:
                    print("Cuenta no encontrada.")
                    
            elif opcion == 5:
                break
                
            else:
                print("Opción no válida. Intente nuevamente.")
                
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Se produjo un error inesperado: {e}")

if __name__ == "__main__":
    main()
