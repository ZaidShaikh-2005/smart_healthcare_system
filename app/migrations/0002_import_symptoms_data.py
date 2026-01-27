from django.db import migrations
import pandas as pd
from pathlib import Path

def import_symptoms(apps, schema_editor):
    Symptom = apps.get_model("app", "Symptom")

    file_path = Path("archive/dataset.csv")

    if not file_path.exists():
        print("❌ dataset.csv not found")
        return

    df = pd.read_csv(file_path)

    symptom_columns = [c for c in df.columns if c.startswith("Symptom")]

    unique_symptoms = set()

    for col in symptom_columns:
        for val in df[col].dropna():
            unique_symptoms.add(val)

    for symptom in unique_symptoms:
        Symptom.objects.get_or_create(
            name=str(symptom).replace("_", " ").title()
        )

    print("✅ Symptoms imported successfully")


class Migration(migrations.Migration):

    dependencies = [
        ("app", "000X_previous_migration"),  # ← yahan apna actual number
    ]

    operations = [
        migrations.RunPython(import_symptoms),
    ]
