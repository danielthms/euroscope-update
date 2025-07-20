import csv
import re
from pathlib import Path
from typing import Dict, List


class ProfileUpdater:
    def __init__(self, config):
        self.config = config

    def update_all_profiles(self, package_info: Dict[str, str]):
        print("👤 Updating profiles...")

        fir_code = package_info["fir"]
        base_dir = self.config.euroscope_docs

        if self.config.use_subdirs:
            base_dir = base_dir / fir_code

        self._update_observer_callsign(fir_code, base_dir)

        for prf_file in base_dir.rglob("*.prf"):
            print(f"   Processing {prf_file.name}")
            self._update_profile_file(prf_file, package_info)

        self._update_hoppie_code(package_info, base_dir)

    def _update_observer_callsign(self, fir_code: str, base_dir: Path):
        print("   Setting observer callsign...")

        if not self.config.initials:
            print("      ⚠️  No initials configured, skipping observer callsign update")
            return

        settings_dir = base_dir / fir_code / "Settings"
        if not settings_dir.exists():
            print(f"      ⚠️  Settings directory not found: {settings_dir}")
            return

        profile_files = list(settings_dir.rglob("*Profil*.txt"))

        if not profile_files:
            print("      ⚠️  No profile definition files found")
            return

        observer_callsign = self.config.observer_callsign

        for profile_file in profile_files:
            try:
                with open(profile_file, "r", encoding="iso-8859-1") as f:
                    content = f.read()

                pattern = r"PROFILE:.+_OBS:"
                replacement = f"PROFILE:{observer_callsign}:"

                new_content = re.sub(pattern, replacement, content)

                if new_content != content:
                    with open(profile_file, "w", encoding="iso-8859-1") as f:
                        f.write(new_content)
                    print(
                        f"      ✓ Updated observer callsign to {observer_callsign} in {profile_file.name}"
                    )

            except Exception as e:
                print(
                    f"      ⚠️  Error updating observer callsign in {profile_file.name}: {e}"
                )

    def _update_profile_file(self, prf_file: Path, package_info: Dict[str, str]):
        profile_data = []
        session_attributes = {
            "realname": False,
            "certificate": False,
            "password": False,
            "rating": False,
            "server": False,
            "tovatsim": False,
        }
        vccs_attributes = {
            "Ts3NickName": False,
            "Ts3G2GPtt": False,
            "PlaybackMode": False,
            "PlaybackDevice": False,
            "CaptureMode": False,
            "CaptureDevice": False,
        }

        try:
            with open(prf_file, "r", encoding="iso-8859-1") as f:
                reader = csv.reader(f, delimiter="\t")
                for i, line in enumerate(reader):
                    if not line:
                        profile_data.append(line)
                        continue

                    if len(line) >= 2:
                        if line[0] == "LastSession" and line[1] in session_attributes:
                            session_attributes[line[1]] = i
                        elif line[0] == "TeamSpeakVccs" and line[1] in vccs_attributes:
                            vccs_attributes[line[1]] = i

                        if line[0] == "Settings":
                            self._update_settings_file(line, package_info)

                    profile_data.append(line)

        except Exception as e:
            print(f"      ⚠️  Error reading profile: {e}")
            return

        session_data = {
            "realname": self.config.real_name,
            "certificate": self.config.vatsim_cid,
            "password": self.config.vatsim_password,
            "rating": self.config.rating,
            "server": "AUTOMATIC",
            "tovatsim": "1",
        }

        vccs_data = {
            "Ts3NickName": self.config.vatsim_cid,
            "Ts3G2GPtt": self.config.get("VCCS", "ptt"),
            "PlaybackMode": self.config.get("VCCS", "mode"),
            "PlaybackDevice": self.config.get("VCCS", "playback"),
            "CaptureMode": self.config.get("VCCS", "mode"),
            "CaptureDevice": self.config.get("VCCS", "capture"),
        }

        for attr, value in session_data.items():
            profile_data = self._add_or_update_attribute(
                profile_data, "LastSession", attr, value, session_attributes[attr]
            )

        for attr, value in vccs_data.items():
            if value:
                profile_data = self._add_or_update_attribute(
                    profile_data, "TeamSpeakVccs", attr, value, vccs_attributes[attr]
                )

        try:
            with open(prf_file, "w", newline="", encoding="iso-8859-1") as f:
                writer = csv.writer(f, delimiter="\t")
                for line in profile_data:
                    writer.writerow(line)
        except Exception as e:
            print(f"      ⚠️  Error writing profile: {e}")

    def _add_or_update_attribute(
        self, data: List, section: str, key: str, value: str, existing_line: int
    ) -> List:
        if existing_line is not False:
            if len(data[existing_line]) >= 3:
                data[existing_line][2] = value
            else:
                data[existing_line].append(value)
        else:
            data.append([section, key, value])

        return data

    def _update_settings_file(self, settings_line: List, package_info: Dict[str, str]):
        if len(settings_line) < 3:
            return

        settings_path = Path(settings_line[2])
        if settings_path == Path("."):
            return

        if settings_path.parts[0] == ".":
            settings_path = Path(*settings_path.parts[1:])

        base_dir = self.config.euroscope_docs
        if self.config.use_subdirs:
            base_dir = base_dir / package_info["fir"]

        full_path = base_dir / settings_path

        if not full_path.exists():
            return

        if settings_line[1] == "SettingsfileSYMBOLOGY":
            self._update_symbology_file(full_path)
        elif settings_line[1] == "SettingsfilePROFILE":
            self._update_profiles_file(full_path)
        elif self.config.text_size and "General" in settings_line[1]:
            self._update_text_size_in_file(full_path)

    def _update_symbology_file(self, symbology_path: Path):
        if not self.config.text_size:
            return

        try:
            settings = []
            with open(symbology_path, "r", encoding="iso-8859-1") as f:
                reader = csv.reader(f, delimiter=":")
                settings = list(reader)

            if not settings or "SYMBOLOGY" not in settings[0][0]:
                return

            rows_to_update = list(range(25, 63)) + [86, 87, 88, 90, 92, 93]

            for row in rows_to_update:
                if row < len(settings) and len(settings[row]) >= 4:
                    settings[row][3] = self.config.text_size

            with open(symbology_path, "w", newline="", encoding="iso-8859-1") as f:
                writer = csv.writer(f, delimiter=":")
                writer.writerows(settings)

            print(f"      ✓ Updated symbology text size: {self.config.text_size}")

        except Exception as e:
            print(f"      ⚠️  Error updating symbology: {e}")

    def _update_profiles_file(self, profiles_path: Path):
        if not self.config.initials:
            return

        try:
            settings = []
            with open(profiles_path, "r", encoding="iso-8859-1") as f:
                reader = csv.reader(f, delimiter=":")
                settings = list(reader)

            for line in settings:
                if len(line) >= 2 and line[0] == "PROFILE" and line[1].endswith("_OBS"):
                    line[1] = f"{self.config.initials}_OBS"

            with open(profiles_path, "w", newline="", encoding="iso-8859-1") as f:
                writer = csv.writer(f, delimiter=":")
                writer.writerows(settings)

            print(f"      ✓ Updated observer callsign: {self.config.observer_callsign}")

        except Exception as e:
            print(f"      ⚠️  Error updating profiles: {e}")

    def _update_text_size_in_file(self, file_path: Path):
        if not self.config.text_size:
            return

        try:
            settings = []
            with open(file_path, "r", encoding="iso-8859-1") as f:
                reader = csv.reader(f, delimiter=":")
                settings = list(reader)

            for line in settings:
                if (
                    len(line) >= 2
                    and line[0] == "m_Column"
                    and len(line) > 1
                    and line[-1] != "0.0"
                ):
                    line[-1] = self.config.text_size

            with open(file_path, "w", newline="", encoding="iso-8859-1") as f:
                writer = csv.writer(f, delimiter=":")
                writer.writerows(settings)

            print(f"      ✓ Updated text size in {file_path.name}")

        except Exception as e:
            print(f"      ⚠️  Error updating text size: {e}")

    def _update_hoppie_code(self, package_info: Dict[str, str], base_dir: Path):
        if not self.config.hoppie_code:
            return

        fir_code = package_info['fir']

        hoppie_files = list(base_dir.rglob("**/TopSkyCPDLChoppieCode.txt"))

        if not hoppie_files:
            print(f"   ⚠️  No Hoppie code files found in {fir_code}")
            return

        files_updated = 0
        for hoppie_file in hoppie_files:
            try:
                with open(hoppie_file, 'w', encoding='utf-8') as f:
                    f.write(self.config.hoppie_code)
                print(f"   ✓ Updated Hoppie code in {hoppie_file.relative_to(base_dir)}")
                files_updated += 1
            except Exception as e:
                print(f"   ⚠️  Error updating Hoppie code in {hoppie_file.name}: {e}")

        if files_updated > 0:
            print(f"   ✓ Updated Hoppie code in {files_updated} files")
