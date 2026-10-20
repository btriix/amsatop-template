import os
from typing import List
from amsatop import Htop, Process, TaskType

class Amsatop(Htop):
    def __init__(self):
        super().__init__()

    def get_processes(self) -> List[Process]:
        procesos = []
        PF_KTHREAD = 0x00200000  # La constante mágica de los profesores
        
        for carpeta in os.listdir(self.proc_folder):
            if not carpeta.isdigit():
                continue
                
            pid_principal = int(carpeta)
            ruta_proceso = f"{self.proc_folder}/{carpeta}"
            ruta_stat = f"{ruta_proceso}/stat"
            
            if not os.path.exists(ruta_stat):
                continue
                
            try:
                with open(ruta_stat, "r") as f:
                    contenido_stat = f.read()
                    
                # 1. Extraemos el nombre entre paréntesis
                inicio = contenido_stat.find("(")
                fin = contenido_stat.rfind(")")
                comando = contenido_stat[inicio+1:fin]
                
                # 2. Leemos los flags (es la palabra nº 6 después del paréntesis)
                resto_stat = contenido_stat[fin+1:].split()
                flags = int(resto_stat[6])
                
                # 3. Aplicamos la fórmula exacta de los profesores
                es_kthread = (flags & PF_KTHREAD) != 0
                
                tipo_proc = TaskType.KTHREAD if es_kthread else TaskType.PROCESS
                procesos.append(Process(pid=pid_principal, command=comando, type=tipo_proc, priority=None))
                
                # 4. Buscamos hilos dentro de la carpeta task
                ruta_task = f"{ruta_proceso}/task"
                if os.path.exists(ruta_task):
                    for hilo in os.listdir(ruta_task):
                        if not hilo.isdigit():
                            continue
                            
                        tid = int(hilo)
                        if tid == pid_principal:
                            continue
                            
                        try:
                            with open(f"{ruta_task}/{hilo}/stat", "r") as f_hilo:
                                cont_hilo = f_hilo.read()
                                
                            inicio_h = cont_hilo.find("(")
                            fin_h = cont_hilo.rfind(")")
                            comando_hilo = cont_hilo[inicio_h+1:fin_h]
                            
                            procesos.append(Process(pid=tid, command=comando_hilo, type=TaskType.THREAD, priority=None))
                        except FileNotFoundError:
                            continue
                            
            except Exception:
                continue
                
        return procesos

    def get_priorities(self) -> List[Process]:
        raise NotImplementedError("Prac-2.2 implementation needed")

    def get_hup(self) -> List[Process]:
        raise NotImplementedError("Prac-2.3 implementation needed")
