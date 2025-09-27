import docx
import json
import ollama
import pandas as pd
import matplotlib.pyplot as plt

MODEL_NAME = "codellama:7b-instruct"  # tu modelo Ollama

# -----------------------------
# 1. Leer DOCX
# -----------------------------
def read_docx(file_path):
    doc = docx.Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return paragraphs

# -----------------------------
# 2. Parsear bloques con Ollama
# -----------------------------
def parse_with_ollama(paragraphs, block_size=5):
    results = {"tareas": [], "objetivos": [], "casos_de_uso": [], "metricas": []}

    for i in range(0, len(paragraphs), block_size):
        block = "\n".join(paragraphs[i:i+block_size])
        prompt = f"""
        Extrae en JSON:
        - tareas (nombre, inicio, fin, responsable)
        - objetivos
        - casos_de_uso
        - métricas relevantes

        Texto:
        {block}
        """
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response["message"]["content"]
            data = json.loads(content)
            # Combinar resultados
            for key in results.keys():
                if key in data:
                    results[key].extend(data[key])
        except Exception as e:
            print(f"⚠ Error parseando bloque {i}-{i+block_size}:", e)
    
    return results

# -----------------------------
# 3. Generar gráfico de ejemplo
# -----------------------------
def plot_tareas(tareas):
    if not tareas:
        print("No hay tareas para graficar.")
        return

    df = pd.DataFrame(tareas)
    if "inicio" in df.columns and "fin" in df.columns and "nombre" in df.columns:
        df["inicio"] = pd.to_datetime(df["inicio"])
        df["fin"] = pd.to_datetime(df["fin"])
        df["duracion"] = (df["fin"] - df["inicio"]).dt.days
        plt.figure(figsize=(10,6))
        plt.barh(df["nombre"], df["duracion"])
        plt.xlabel("Duración (días)")
        plt.title("Duración de Tareas")
        plt.tight_layout()
        plt.show()
    else:
        print("Las columnas esperadas no están presentes en las tareas.")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    doc_path_calidad = "D12-Plan de SQA-GRCU-4BYTES.docx"
    paragraphs_calidad = read_docx(doc_path_calidad)
    print("Procesando Plan de Calidad...")
    data_calidad = parse_with_ollama(paragraphs_calidad)
    print("Resultados Plan de Calidad:", data_calidad)

    # Generar gráfico de ejemplo de tareas
    plot_tareas(data_calidad.get("tareas", []))
