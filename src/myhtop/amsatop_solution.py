import os
from typing import List
from amsatop import Htop, Process, TaskType

class Amsatop(Htop):
    def __init__(self):
        super().__init__()

    def get_processes(self) -> List[Process]:
        procesos = []
        PF_KTHREAD = 0x00200000
        
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
                    
                inicio = contenido_stat.find("(")
                fin = contenido_stat.rfind(")")
                comando = contenido_stat[inicio+1:fin]
                
                resto_stat = contenido_stat[fin+1:].split()
                flags = int(resto_stat[6])
                
                es_kthread = (flags & PF_KTHREAD) != 0
                tipo_proc = TaskType.KTHREAD if es_kthread else TaskType.PROCESS
                procesos.append(Process(pid=pid_principal, command=comando, type=tipo_proc, priority=None))
                
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
        procesos = []
        PF_KTHREAD = 0x00200000
        
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
                    
                inicio = contenido_stat.find("(")
                fin = contenido_stat.rfind(")")
                comando = contenido_stat[inicio+1:fin]
                
                resto_stat = contenido_stat[fin+1:].split()
                flags = int(resto_stat[6])
                prioridad = int(resto_stat[15])
                
                es_kthread = (flags & PF_KTHREAD) != 0
                tipo_proc = TaskType.KTHREAD if es_kthread else TaskType.PROCESS
                procesos.append(Process(pid=pid_principal, command=comando, type=tipo_proc, priority=prioridad))
                
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
                            
                            resto_stat_hilo = cont_hilo[fin_h+1:].split()
                            prioridad_hilo = int(resto_stat_hilo[15])
                            
                            procesos.append(Process(pid=tid, command=comando_hilo, type=TaskType.THREAD, priority=prioridad_hilo))
                        except FileNotFoundError:
                            continue
            except Exception:
                continue
                
        return procesos

    def get_hup(self) -> List[Process]:
        procesos = []
        PF_KTHREAD = 0x00200000
        SIGHUP_MASK = 1  # Máscara para la señal 1
        
        for carpeta in os.listdir(self.proc_folder):
            if not carpeta.isdigit():
                continue
                
            pid_principal = int(carpeta)
            ruta_proceso = f"{self.proc_folder}/{carpeta}"
            ruta_stat = f"{ruta_proceso}/stat"
            ruta_status = f"{ruta_proceso}/status"
            
            if not os.path.exists(ruta_stat) or not os.path.exists(ruta_status):
                continue
                
            try:
                # 1. Leemos stat para nombre, tipo y prioridad
                with open(ruta_stat, "r") as f:
                    contenido_stat = f.read()
                    
                inicio = contenido_stat.find("(")
                fin = contenido_stat.rfind(")")
                comando = contenido_stat[inicio+1:fin]
                
                resto_stat = contenido_stat[fin+1:].split()
                flags = int(resto_stat[6])
                prioridad = int(resto_stat[15])
                
                es_kthread = (flags & PF_KTHREAD) != 0
                tipo_proc = TaskType.KTHREAD if es_kthread else TaskType.PROCESS
                
                # 2. Leemos status para ver si ignora SIGHUP
                ignora_hup = False
                with open(ruta_status, "r") as f:
                    for linea in f:
                        if linea.startswith("SigIgn:"):
                            # Extraemos el valor hexa (ej: "0000000000000005") y lo pasamos a entero base 16
                            valor_hexa = linea.split(":")[1].strip()
                            sigign = int(valor_hexa, 16)
                            if (sigign & SIGHUP_MASK) != 0:
                                ignora_hup = True
                            break
                            
                # SOLO lo añadimos si ignora SIGHUP
                if ignora_hup:
                    procesos.append(Process(pid=pid_principal, command=comando, type=tipo_proc, priority=prioridad))
                
                # 3. Hacemos lo mismo para los hilos
                ruta_task = f"{ruta_proceso}/task"
                if os.path.exists(ruta_task):
                    for hilo in os.listdir(ruta_task):
                        if not hilo.isdigit():
                            continue
                            
                        tid = int(hilo)
                        if tid == pid_principal:
                            continue
                            
                        ruta_stat_hilo = f"{ruta_task}/{hilo}/stat"
                        ruta_status_hilo = f"{ruta_task}/{hilo}/status"
                        
                        try:
                            with open(ruta_stat_hilo, "r") as f_hilo:
                                cont_hilo = f_hilo.read()
                                
                            inicio_h = cont_hilo.find("(")
                            fin_h = cont_hilo.rfind(")")
                            comando_hilo = cont_hilo[inicio_h+1:fin_h]
                            
                            resto_stat_hilo = cont_hilo[fin_h+1:].split()
                            prioridad_hilo = int(resto_stat_hilo[15])
                            
                            # Comprobamos SIGHUP en el hilo
                            ignora_hup_hilo = False
                            with open(ruta_status_hilo, "r") as f_sh:
                                for linea in f_sh:
                                    if linea.startswith("SigIgn:"):
                                        valor_hexa_hilo = linea.split(":")[1].strip()
                                        sigign_hilo = int(valor_hexa_hilo, 16)
                                        if (sigign_hilo & SIGHUP_MASK) != 0:
                                            ignora_hup_hilo = True
                                        break
                                        
                            if ignora_hup_hilo:
                                procesos.append(Process(pid=tid, command=comando_hilo, type=TaskType.THREAD, priority=prioridad_hilo))
                        except FileNotFoundError:
                            continue
            except Exception:
                continue
                
        return procesos
