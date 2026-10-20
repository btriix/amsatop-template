from typing import List
import os

from amsatop import Htop, Process, TaskType

class Amsatop(Htop):
    def __init__(self):
        super().__init__()

    def get_processes(self) -> List[Process]:
        procesos = []

        for carpeta in os.listdir(self.proc_folder):
            if not carpeta.isdigit():
                continue

            pid = int(carpeta)
            ruta_proceso = f"{self.proc_folder}/{carpeta}"

            # 1. Leemos el comando
            ruta_comm = f"{ruta_proceso}/comm"
            if not os.path.exists(ruta_comm):
                continue

            with open(ruta_comm, "r") as f:
                comando = f.read().strip()

            # 2. Comprobamos si es KTHREAD
            es_kthread = False
            ruta_cmdline = f"{ruta_proceso}/cmdline"
            if os.path.exists(ruta_cmdline):
                with open(ruta_cmdline, "r") as f:
                    if f.read().strip() == "":
                        es_kthread = True

            tipo_proc = TaskType.KTHREAD if es_kthread else TaskType.PROCESS

            # Añadimos el proceso (fíjate que usamos 'command=')
            procesos.append(Process(pid=pid, command=comando, type=tipo_proc, priority=None))

            # 3. Buscamos los hilos
            ruta_task = f"{ruta_proceso}/task"
            if os.path.exists(ruta_task):
                for hilo in os.listdir(ruta_task):
                    if not hilo.isdigit():
                        continue

                    tid = int(hilo)
                    if tid == pid:
                        continue # Saltamos el principal, ya lo hemos añadido

                    ruta_comm_hilo = f"{ruta_task}/{hilo}/comm"
                    if os.path.exists(ruta_comm_hilo):
                        with open(ruta_comm_hilo, "r") as f:
                            comando_hilo = f.read().strip()
                        # El hilo se añade poniendo su 'tid' en el campo 'pid'
                        procesos.append(Process(pid=tid, command=comando_hilo, type=TaskType.THREAD, priority=None))

        return procesos


    def get_priorities(self) -> List[Process]:
        raise NotImplementedError("Prac-2.2 implementation needed")

    def get_hup(self) -> List[Process]:
        raise NotImplementedError("Prac-2.3 implementation needed")
