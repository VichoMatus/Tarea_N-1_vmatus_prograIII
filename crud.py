from models import Personaje, Mision, MisionPersonaje
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from shemas import PersonajeCreate, MisionCreate
from cola import ColaMisiones

# Crear nuevo personaje
def crear_personaje(personaje: PersonajeCreate):  # Ahora PersonajeCreate
    db = SessionLocal()
    db_personaje = Personaje(name=personaje.name)  # El modelo SQLAlchemy sigue recibiendo solo 'name'
    db.add(db_personaje)
    db.commit()
    db.refresh(db_personaje)
    db.close()
    return db_personaje  # Regresa el modelo de SQLAlchemy que se convertirá a Pydantic

# Crear nueva misión para un personaje
def crear_mision(id: int, mision: MisionCreate):  # Ahora MisionCreate
    db = SessionLocal()
    db_mision = Mision(name=mision.name, description=mision.description)
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)

    # Agregar misión al personaje
    mision_personaje = MisionPersonaje(personaje_id=id, mision_id=db_mision.id)
    db.add(mision_personaje)
    db.commit()

    db.close()
    return db_mision

# Aceptar misión (encolar)
def aceptar_mision(id: int, id_mision: int, cola_misiones: ColaMisiones):
    db = SessionLocal()
    mision = db.query(Mision).filter(Mision.id == id_mision).first()
    if not mision:
        db.close()
        raise HTTPException(status_code=404, detail="Misión no encontrada")
    
    # Agregar misión a la cola
    cola_misiones.enqueue(mision)
    db.close()
    return {"message": "Misión aceptada"}

# Completar misión (desencolar)
def completar_mision(id: int, id_mision: int, cola_misiones: ColaMisiones):
    mision = cola_misiones.dequeue()
    if not mision:
        raise HTTPException(status_code=404, detail="No hay misiones en cola")
    return {"message": f"Misión completada: {mision.name}"}

# Listar misiones en orden FIFO
def listar_misiones(id: int, cola_misiones: ColaMisiones):
    return {"misiones": [m.name for m in cola_misiones.cola]}
