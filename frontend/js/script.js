// 监听表单提交事件
document.getElementById('thermalForm').addEventListener('submit', function(e) {
    e.preventDefault(); // 阻止默认表单提交

    // 1. 获取表单输入值
    const formData = {
        width: document.getElementById('width').value,
        height: document.getElementById('height').value,
        frame_ratio: document.getElementById('frame_ratio').value,
        glass_ug: document.getElementById('glass_ug').value,
        frame_upper1: document.getElementById('frame_upper1').value,
        frame_upper2: document.getElementById('frame_upper2').value,
        frame_lower1: document.getElementById('frame_lower1').value,
        frame_lower2: document.getElementById('frame_lower2').value,
        frame_left: document.getElementById('frame_left').value,
        frame_right: document.getElementById('frame_right').value,
        frame_mullion: document.getElementById('frame_mullion').value,
        psi: document.getElementById('psi').value
    };

    // 2. 调用后端API
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // 3. 处理返回结果
        if (data.success) {
            // 显示结果区域
            document.getElementById('resultArea').style.display = 'block';
            // 填充结果
            document.getElementById('total_area').textContent = data.data.total_area;
            document.getElementById('frame_area').textContent = data.data.frame_area;
            document.getElementById('glass_area').textContent = data.data.glass_area;
            document.getElementById('avg_uf').textContent = data.data.avg_uf;
            document.getElementById('glass_ug_result').textContent = data.data.glass_ug;
            document.getElementById('uw').textContent = data.data.uw;
            document.getElementById('glass_edge_length').textContent = data.data.glass_edge_length;
        } else {
            alert('计算失败：' + data.error);
        }
    })
    .catch(error => {
        alert('请求失败：' + error);
    });
});