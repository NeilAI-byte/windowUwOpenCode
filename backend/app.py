from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dataclasses import dataclass
from typing import List
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(BASE_DIR, '..', 'frontend', 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(BASE_DIR, '..', 'frontend', 'js'), filename)

# ====================== 国标合规的数据结构定义 ======================
@dataclass
class FrameComponent:
    name: str
    length: float
    visual_width: float
    uf: float

@dataclass
class WindowParams:
    window_width: float
    window_height: float
    glass_ug: float
    psi: float
    glass_edge_length: float
    frame_components: List[FrameComponent]

# ====================== 国标合规的热工计算核心类 ======================
class WindowThermalCalculator:
    def __init__(self, params: WindowParams):
        self.params = params
        self.total_area = round(params.window_width * params.window_height, 6)
        self.frame_calc_results = self._calc_frame_components()

    def _calc_frame_components(self) -> list:
        results = []
        for comp in self.params.frame_components:
            area = round(comp.length * comp.visual_width, 6)
            area_uf = round(area * comp.uf, 6)
            results.append({
                "name": comp.name,
                "area": area,
                "uf": comp.uf,
                "area_uf": area_uf
            })
        return results

    def get_total_frame_area(self) -> float:
        return round(sum([item["area"] for item in self.frame_calc_results]), 6)

    def get_total_frame_heat(self) -> float:
        return round(sum([item["area_uf"] for item in self.frame_calc_results]), 6)

    def get_glass_area(self) -> float:
        return round(self.total_area - self.get_total_frame_area(), 6)

    def calculate_uw(self) -> float:
        total_frame_heat = self.get_total_frame_heat()
        glass_heat = round(self.get_glass_area() * self.params.glass_ug, 6)
        linear_heat = round(self.params.psi * self.params.glass_edge_length, 6)
        total_numerator = total_frame_heat + glass_heat + linear_heat
        uw = round(total_numerator / self.total_area, 2)
        return uw

    def get_all_results(self) -> dict:
        return {
            "total_area": self.total_area,
            "total_frame_area": self.get_total_frame_area(),
            "glass_area": self.get_glass_area(),
            "total_frame_heat": self.get_total_frame_heat(),
            "glass_heat": round(self.get_glass_area() * self.params.glass_ug, 6),
            "linear_heat": round(self.params.psi * self.params.glass_edge_length, 6),
            "total_numerator": round(self.get_total_frame_heat() + self.get_glass_area() * self.params.glass_ug + self.params.psi * self.params.glass_edge_length, 6),
            "uw": self.calculate_uw(),
            "frame_components_detail": self.frame_calc_results
        }

# ====================== 后端API接口 ======================
@app.route('/api/calculate', methods=['POST'])
def calculate_thermal():
    try:
        data = request.get_json()
        required_fields = ["window_width", "window_height", "glass_ug", "psi", "glass_edge_length", "frame_components"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必填参数：{field}"}), 400
        
        frame_components = []
        for comp in data["frame_components"]:
            frame_components.append(FrameComponent(
                name=comp["name"],
                length=float(comp["length"]),
                visual_width=float(comp["visual_width"]),
                uf=float(comp["uf"])
            ))
        
        params = WindowParams(
            window_width=float(data["window_width"]),
            window_height=float(data["window_height"]),
            glass_ug=float(data["glass_ug"]),
            psi=float(data["psi"]),
            glass_edge_length=float(data["glass_edge_length"]),
            frame_components=frame_components
        )
        calculator = WindowThermalCalculator(params)
        results = calculator.get_all_results()
        return jsonify({"success": True, "data": results}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)