import json
import os


class ArtifactManager:

    def __init__(self):
        self.artifacts = []

    def add_artifact(self, artifact_path):
        if os.path.exists(artifact_path):
            self.artifacts.append(artifact_path)

    def export_manifest(self, run_dir):
        artifacts_dir = os.path.join(run_dir, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)

        manifest_path = os.path.join(artifacts_dir, "artifact_manifest.json")

        manifest = {
            "run_dir": run_dir,
            "artifact_count": len(self.artifacts),
            "artifacts": self.artifacts,
        }

        try:
            with open(manifest_path, "w") as file:
                json.dump(manifest, file, indent=2)
        except OSError as e:
            print(f"[WARN] Failed to write artifact manifest: {e}")
