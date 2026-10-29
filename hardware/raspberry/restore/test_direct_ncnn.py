import json,time,statistics
from pathlib import Path
import cv2
from agave_ncnn import AgaveNCNN
cv2.setNumThreads(1)
root=Path('/home/bioiot/agave_benchmark_20260921')
reference=json.loads((root/'backend_comparison.json').read_text())['ncnn']['records']
t=time.perf_counter();model=AgaveNCNN(root/'best_ncnn_model');load=time.perf_counter()-t
records=[]
for row in reference:
    image=cv2.resize(cv2.imread(str(root/'images'/row['image'])),(640,360))
    t=time.perf_counter(); boxes=model.predict(image);elapsed=time.perf_counter()-t
    error=0.0
    assert len(boxes)==len(row['boxes']), (row['image'],len(boxes),len(row['boxes']))
    for box,cls,score in boxes:
        if row['boxes']:
            delta=min(max(abs(a-b) for a,b in zip(box+[score,cls],ref)) for ref in row['boxes'])
            error=max(error,delta)
    assert error<0.1,(row['image'],error)
    records.append({'image':row['image'],'seconds':elapsed,'boxes':len(boxes),'max_numeric_difference':error})
    print(records[-1],flush=True)
summary={'load_seconds':load,'mean_seconds':statistics.mean(r['seconds'] for r in records),'records':records}
(root/'direct_ncnn_comparison.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
