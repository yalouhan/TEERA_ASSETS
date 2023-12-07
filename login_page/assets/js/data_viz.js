import * as THREE from 'three';
import Stats from 'three/addons/libs/stats.module.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class ParticleSystem {
    constructor(maxParticleCount, xOffset, yOffset, zOffset, r, group) {
        this.maxParticleCount = maxParticleCount;
        this.particlesData = [];
        this.particlePositions = new Float32Array(maxParticleCount * 3);
        this.r = r;
        this.rHalf = r / 2;
        this.xOffset = xOffset;
        this.yOffset = yOffset;
        this.zOffset = zOffset;
        this.group = group;
        this.initParticles();
        this.createParticles();
        this.createBoxMesh();
        this.initLines();
    }

    initParticles() {
        for (let i = 0; i < this.maxParticleCount; i++) {
            const x = this.xOffset + (Math.random() * this.r - this.rHalf);
            const y = this.yOffset + (Math.random() * this.r - this.rHalf);
            const z = this.zOffset + (Math.random() * this.r - this.rHalf);

            this.particlePositions[i * 3] = x;
            this.particlePositions[i * 3 + 1] = y;
            this.particlePositions[i * 3 + 2] = z;

            this.particlesData.push({
                velocity: new THREE.Vector3(-0.02 + Math.random() * 0.04, -0.02 + Math.random() * 0.04, -0.02 + Math.random() * 0.04),
                numConnections: 0
            });
        }
    }

    createParticles() {
        const pMaterial = new THREE.PointsMaterial({
            color: 0xFF09E6,
            size: 4,
            transparent: false,
            sizeAttenuation: false
        });

        this.particles = new THREE.BufferGeometry();
        this.particles.setDrawRange(0, this.maxParticleCount);
        this.particles.setAttribute('position', new THREE.BufferAttribute(this.particlePositions, 3).setUsage(THREE.DynamicDrawUsage));
        this.pointCloud = new THREE.Points(this.particles, pMaterial);
        this.group.add(this.pointCloud);
    }

    createBoxMesh() {
        const boxGeometry = new THREE.BoxGeometry(this.r, this.r, this.r);
        const edges = new THREE.EdgesGeometry(boxGeometry);
        this.boxMeshMaterial = new THREE.LineBasicMaterial({
            color: 0xEAEAEA,
            transparent: true,
            opacity: effectController.meshOpacity
        });
        const lineSegments = new THREE.LineSegments(edges, this.boxMeshMaterial);
        lineSegments.position.x = this.xOffset;
        lineSegments.position.y = this.yOffset;
        lineSegments.position.z = this.zOffset;
        this.group.add(lineSegments);
    }


    updateMeshOpacity(opacity) {
        console.log("Updating mesh opacity to:", opacity);
        if (this.boxMeshMaterial) {
            this.boxMeshMaterial.opacity = opacity;
            this.boxMeshMaterial.needsUpdate = true;
        }
    }


    initLines() {
        const segments = this.maxParticleCount * this.maxParticleCount;
        this.positions = new Float32Array(segments * 3);
        this.colors = new Float32Array(segments * 3);

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3).setUsage(THREE.DynamicDrawUsage));
        geometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3).setUsage(THREE.DynamicDrawUsage));

        const material = new THREE.LineBasicMaterial({
            vertexColors: true,
            transparent: false
        });

        this.linesMesh = new THREE.LineSegments(geometry, material);
        this.group.add(this.linesMesh);
    }

    updateLineOpacity(LineOpacity) {
        if (this.linesMesh) {
            const newMaterial = new THREE.LineBasicMaterial({
                vertexColors: true,
                transparent: true,
                opacity: LineOpacity
            });
            this.linesMesh.material.dispose();
            this.linesMesh.material = newMaterial;
        }
    }

    update(minDistance) {
        let vertexpos = 0;
        let colorpos = 0;
        let numConnected = 0;

        for (let i = 0; i < this.maxParticleCount; i++) {
            this.particlesData[i].numConnections = 0;
        }

        for (let i = 0; i < this.maxParticleCount; i++) {
            const particleData = this.particlesData[i];

            this.particlePositions[i * 3] += particleData.velocity.x;
            this.particlePositions[i * 3 + 1] += particleData.velocity.y;
            this.particlePositions[i * 3 + 2] += particleData.velocity.z;

            if (this.particlePositions[i * 3] < this.xOffset - this.rHalf || this.particlePositions[i * 3] > this.xOffset + this.rHalf) {
                particleData.velocity.x = -particleData.velocity.x;
            }
            if (this.particlePositions[i * 3 + 1] < this.yOffset - this.rHalf || this.particlePositions[i * 3 + 1] > this.yOffset + this.rHalf) {
                particleData.velocity.y = -particleData.velocity.y;
            }
            if (this.particlePositions[i * 3 + 2] < this.zOffset - this.rHalf || this.particlePositions[i * 3 + 2] > this.zOffset + this.rHalf) {
                particleData.velocity.z = -particleData.velocity.z;
            }

            for (let j = i + 1; j < this.maxParticleCount; j++) {
                const particleDataB = this.particlesData[j];
                if (particleData.numConnections >= 20 || particleDataB.numConnections >= 20)
                    continue;

                const dx = this.particlePositions[i * 3] - this.particlePositions[j * 3];
                const dy = this.particlePositions[i * 3 + 1] - this.particlePositions[j * 3 + 1];
                const dz = this.particlePositions[i * 3 + 2] - this.particlePositions[j * 3 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (dist < minDistance) {
                    particleData.numConnections++;
                    particleDataB.numConnections++;

                    const alpha = 1.0 - dist / minDistance;

                    this.positions[vertexpos++] = this.particlePositions[i * 3];
                    this.positions[vertexpos++] = this.particlePositions[i * 3 + 1];
                    this.positions[vertexpos++] = this.particlePositions[i * 3 + 2];

                    this.positions[vertexpos++] = this.particlePositions[j * 3];
                    this.positions[vertexpos++] = this.particlePositions[j * 3 + 1];
                    this.positions[vertexpos++] = this.particlePositions[j * 3 + 2];

                    this.colors[colorpos++] = alpha;
                    this.colors[colorpos++] = alpha;
                    this.colors[colorpos++] = alpha;

                    this.colors[colorpos++] = alpha;
                    this.colors[colorpos++] = alpha;
                    this.colors[colorpos++] = alpha;

                    numConnected++;
                }
            }
        }
        this.particles.attributes.position.needsUpdate = true;

        this.linesMesh.geometry.setDrawRange(0, numConnected * 2);
        this.linesMesh.geometry.attributes.position.needsUpdate = true;
        this.linesMesh.geometry.attributes.color.needsUpdate = true;
    }
}

let container, stats;
let camera, scene, renderer;
let group;
let particleSystems = [];
let effectController = {
    minDistance: 80,
    lineOpacity: 0.3,
    meshOpacity: 0.1,
    distanceThreshold: 200
};

//储存位置生成连线
let boxMeshPositions = [];

function initGUI() {
    const gui = new GUI();

    gui.add(effectController, 'lineOpacity', 0, 1).onChange(function (value) {
        particleSystems.forEach(system => {
            system.updateLineOpacity(value);
        });
    });

    gui.add(effectController, 'meshOpacity', 0, 1).onChange(function (value) {
        particleSystems.forEach(system => {
            system.updateMeshOpacity(value);
        });
    });

    gui.add(effectController, 'distanceThreshold', 0, 500).onChange(function (value) {
        checkDistanceAndCreateLine(value);
    });

}

function init() {

    initGUI();

    const maxParticleCount = 4;
    const r = 80;
    const xOffsets = [220, 100, 0, -120, -240];
    const yOffsets = [0, 80, 160, 240, 320, 400];
    const zOffsets = [640, 140, 0, -300, -500];

    container = document.getElementById('canvas');
    const aspect = 0.5 * (window.innerWidth / window.innerHeight);
    const d = 20;
    camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 100000);
    camera.position.z = 400;
    const controls = new OrbitControls(camera, container);

    scene = new THREE.Scene();
    group = new THREE.Group();
    scene.add(group);

    xOffsets.forEach(xOffset => {
        yOffsets.forEach(yOffset => {
            zOffsets.forEach(zOffset => {
                particleSystems.push(new ParticleSystem(5 * Math.random() + 2, xOffset, yOffset, zOffset, r, group));
                boxMeshPositions.push({ xOffset, yOffset, zOffset });
            });
        });
    });

    checkDistanceAndCreateLine();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0xFFFFFF, 1);
    container.appendChild(renderer.domElement);

    stats = new Stats();
    container.appendChild(stats.dom);

    window.addEventListener('resize', onWindowResize);
}

function checkDistanceAndCreateLine() {
    let threshold = effectController.distanceThreshold;

    // 清除旧的连线
    let toRemove = [];
    scene.traverse((child) => {
        if (child instanceof THREE.Line) {
            toRemove.push(child);
        }
    });
    toRemove.forEach((child) => {
        scene.remove(child);
    });

    boxMeshPositions.forEach((positionA, i) => {
        for (let j = i + 1; j < boxMeshPositions.length; j++) {
            const positionB = boxMeshPositions[j];
            const dx = positionA.xOffset - positionB.xOffset;
            const dy = positionA.yOffset - positionB.yOffset;
            const dz = positionA.zOffset - positionB.zOffset;
            const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

            if (distance < threshold) {
                createLine(positionA, positionB);
            }
        }
    });
}

function createLine(positionA, positionB) {
    // 创建曲线的控制点
    const midPoint = new THREE.Vector3(
        (positionA.xOffset + positionB.xOffset) / 2,
        (positionA.yOffset + positionB.yOffset) / 2,
        (positionA.zOffset + positionB.zOffset) / 2
    ).add(new THREE.Vector3(Math.random() * 10 - 5, Math.random() * 10 - 5, Math.random() * 10 - 5));

    // 使用 CatmullRomCurve3 创建平滑曲线
    const curve = new THREE.CatmullRomCurve3([
        new THREE.Vector3(positionA.xOffset, positionA.yOffset, positionA.zOffset),
        midPoint,
        new THREE.Vector3(positionB.xOffset, positionB.yOffset, positionB.zOffset)
    ]);

    // 创建曲线的几何形状
    const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(50));
    const material = new THREE.LineBasicMaterial({
        color: 0x0500E3,
        transparent: true,
        opacity: 0.4,
        linewidth: 5
    });

    const line = new THREE.Line(geometry, material);

    // 动画效果
    line.userData = { curve: curve, midPoint: midPoint, originalMidPoint: midPoint.clone() };

    scene.add(line);
}

function animate() {
    requestAnimationFrame(animate);

    // 更新线条以模拟飘动的效果
    scene.children.forEach(child => {
        if (child.userData && child.userData.curve) {
            const midPoint = child.userData.midPoint;
            const originalMidPoint = child.userData.originalMidPoint;

            midPoint.x += (Math.random() - 0.5) * 0.1;
            midPoint.y += (Math.random() - 0.5) * 0.1;
            midPoint.z += (Math.random() - 0.5) * 0.1;

            // 限制中点的移动范围
            if (midPoint.distanceTo(originalMidPoint) > 10) {
                midPoint.copy(originalMidPoint);
            }

            const newCurve = new THREE.CatmullRomCurve3([
                child.userData.curve.points[0],
                midPoint,
                child.userData.curve.points[2]
            ]);

            child.geometry.setFromPoints(newCurve.getPoints(50));
        }
    });


    particleSystems.forEach(system => system.update(effectController.minDistance));
    render();
    stats.update();
}

function render() {
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    checkDistanceAndCreateLine();
    renderer.setSize(window.innerWidth, window.innerHeight);
}


init();
animate();
