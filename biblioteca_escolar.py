#!/usr/bin/env python3
"""Biblioteca escolar — menú por consola. Solo biblioteca estándar (sqlite3)."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "biblioteca.db"


def conectar():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def iniciar_db():
    with conectar() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libro_id INTEGER NOT NULL,
            estudiante TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (libro_id) REFERENCES libros(id)
        );
        """)


def menu():
    print("\n--- Biblioteca escolar ---")
    print("1) Agregar libro")
    print("2) Ver libros")
    print("3) Prestar libro")
    print("4) Devolver libro")
    print("5) Préstamos activos")
    print("0) Salir")
    return input("Opción: ").strip()


def agregar_libro():
    t = input("Título: ").strip()
    a = input("Autor: ").strip()
    if not t or not a:
        print("Título y autor son obligatorios.")
        return
    with conectar() as db:
        db.execute("INSERT INTO libros (titulo, autor) VALUES (?, ?)", (t, a))
    print("Libro registrado.")


def ver_libros():
    with conectar() as db:
        rows = db.execute(
            """SELECT l.id, l.titulo, l.autor,
               (SELECT COUNT(*) FROM prestamos p WHERE p.libro_id=l.id AND p.activo=1) AS en_prestamo
               FROM libros l ORDER BY l.id"""
        ).fetchall()
    if not rows:
        print("No hay libros.")
        return
    for r in rows:
        estado = " (prestado)" if r["en_prestamo"] else " (disponible)"
        print(f"  [{r['id']}] {r['titulo']} — {r['autor']}{estado}")


def prestar():
    ver_libros()
    try:
        lid = int(input("ID del libro: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    nom = input("Nombre del estudiante: ").strip()
    if not nom:
        print("Nombre obligatorio.")
        return
    with conectar() as db:
        if not db.execute("SELECT 1 FROM libros WHERE id=?", (lid,)).fetchone():
            print("Libro no existe.")
            return
        if db.execute(
            "SELECT 1 FROM prestamos WHERE libro_id=? AND activo=1", (lid,)
        ).fetchone():
            print("Ese libro ya está prestado.")
            return
        db.execute(
            "INSERT INTO prestamos (libro_id, estudiante, activo) VALUES (?, ?, 1)",
            (lid, nom),
        )
    print("Préstamo registrado.")


def devolver():
    with conectar() as db:
        rows = db.execute(
            """SELECT p.id, p.estudiante, l.titulo FROM prestamos p
               JOIN libros l ON l.id = p.libro_id WHERE p.activo=1 ORDER BY p.id"""
        ).fetchall()
    if not rows:
        print("No hay préstamos activos.")
        return
    for r in rows:
        print(f"  [{r['id']}] {r['estudiante']} — «{r['titulo']}»")
    try:
        pid = int(input("ID del préstamo: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    with conectar() as db:
        cur = db.execute(
            "UPDATE prestamos SET activo=0 WHERE id=? AND activo=1", (pid,)
        )
        if cur.rowcount == 0:
            print("Préstamo no encontrado o ya devuelto.")
        else:
            print("Devolución registrada.")


def prestamos_activos():
    with conectar() as db:
        rows = db.execute(
            """SELECT p.id, p.estudiante, l.titulo, l.autor FROM prestamos p
               JOIN libros l ON l.id = p.libro_id WHERE p.activo=1 ORDER BY p.id"""
        ).fetchall()
    if not rows:
        print("No hay préstamos activos.")
        return
    for r in rows:
        print(f"  [{r['id']}] {r['estudiante']} — «{r['titulo']}» ({r['autor']})")


def main():
    iniciar_db()
    while True:
        op = menu()
        if op == "1":
            agregar_libro()
        elif op == "2":
            ver_libros()
        elif op == "3":
            prestar()
        elif op == "4":
            devolver()
        elif op == "5":
            prestamos_activos()
        elif op == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
