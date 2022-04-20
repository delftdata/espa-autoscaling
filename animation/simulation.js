class Server {
    constructor(x, y, width, height, color, device_type) {
        this.x_pos = x;
        this.y_pos = y;
        this.width = width;
        this.height = height
        this.color = color
        this.device_type = device_type
    }

    draw(ctx) {
        ctx.beginPath();
        // ctx.strokeStyle = this.color;
        // ctx.lineWidth = 5;
        // ctx.fillStyle = this.color;
        // ctx.fillRect(this.x_pos, this.y_pos, this.height, this.width);
        var img1 = new Image();
        if (this.device_type === "server"){
            img1.src = 'img/server.png';
        } else if (this.device_type === "client"){
            img1.src = 'img/desktop.png';
        } else{
            img1.src = 'img/phone.png';
        }
        ctx.drawImage(img1, this.x_pos, this.y_pos, this.height, this.width);
    }
}

class Circle {
    constructor(x, y, radius, color) {
        this.x_pos = x;
        this.y_pos = y;
        this.radius = radius;
        this.dx = 5;
        this.dy = 0;
        this.color = color
        this.sleep = 90
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 5;
        ctx.arc(this.x_pos, this.y_pos, this.radius, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = this.color;
        ctx.fill();
    }


    move() {
        this.x_pos += this.dx;
        this.y_pos += this.dy;
    }

    bound(x_bound){
        if (this.x_pos >= x_bound){
            this.dx = 0
            this.dy = 0
        }
    }

    velocitiesToPoint(to_x, to_y, velocity){
        var distance_x = Math.abs(to_x - this.x_pos)
        var distance_y = Math.abs(to_y - this.y_pos)
        var angle = Math.atan(distance_y / distance_x)
        var x_velocity = velocity * Math.cos(angle)
        var y_velocity = velocity * Math.sin(angle)
        this.dx = x_velocity

        if (to_y < this.y_pos){
            this.dy = -y_velocity
        }
        else{
            this.dy = y_velocity
        }
    }


}


; (function () {


    function init() {

        canvas = document.getElementById('canvasId');
        ctx = canvas.getContext('2d');
        canvas.style.position = "absolute"; 
        canvas.style.left = "0px";     
        canvas.style.top = "0px";
        canvas.width = innerWidth;         
        canvas.height = innerHeight;

        og_date = new Date();
        date = new Date();
        seconds = date.getSeconds();
        
        position_user_devices = 0.05 * canvas.width

        position_servers = 0.9 * canvas.width

        position_queue_start = 0.2 * canvas.width

        position_queue_end = 0.6 * canvas.width
        

        packet_radius = 5;

        packet_color = 'red';

        pre_queue = [];

        packets = [];

        consumed_packets = [];

        servers = [];

        initial_server = 0;

        initial_user_device = 0;


        // servers
        servers.push(new Server(position_servers, canvas.height*0.4 - 50, 100, 100, "blue", "server"))

        servers.push(new Server(position_servers, canvas.height*0.6 - 50, 100, 100, "blue", "server"))

        // user devices
        servers.push(new Server(position_user_devices, canvas.height*0.75 - 25, 50, 50, "green", "client"))
        servers.push(new Server(position_user_devices, canvas.height*0.5 - 25, 50, 50, "green", "phone"))
        servers.push(new Server(position_user_devices, canvas.height*0.25 - 25, 50, 50, "green", "client"))

        // begin update loop
        window.requestAnimationFrame(update);
    }


    // draws stuff to the screen
    // allows us to separate calculations and drawing
    function draw() {

        // clear the canvas and redraw everything
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.stroke();

        
        // draw some lines
        ctx.beginPath();
        ctx.strokeStyle = "grey"
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 10]);
        ctx.moveTo(position_user_devices, canvas.height / 2);
        ctx.lineTo(position_queue_end, canvas.height / 2);

        // line to queue device 0
        ctx.moveTo(position_user_devices, canvas.height*0.25 - 25);
        ctx.lineTo(position_queue_start, canvas.height / 2);

        // line to queue device 2
        ctx.moveTo(position_user_devices, canvas.height*0.75 + 25);
        ctx.lineTo(position_queue_start, canvas.height / 2);

        // line to server
        ctx.moveTo(position_queue_end, canvas.height / 2);
        ctx.lineTo(position_servers + 50, canvas.height*0.4);

        // line to server
        ctx.moveTo(position_queue_end, canvas.height / 2);
        ctx.lineTo(position_servers + 50, canvas.height*0.6);


        ctx.stroke();

        ctx.setLineDash([]);

        for (var i = 0; i < servers.length; i++) {
            servers[i].draw(ctx);
        }


        // draw packets
        for (var i = 0; i < pre_queue.length; i++) {
            pre_queue[i].draw(ctx);
        }
        for (var i = 0; i < packets.length; i++) {
            packets[i].draw(ctx);
        }
        for (var i = 0; i < consumed_packets.length; i++) {
            consumed_packets[i].draw(ctx);
        }

    }

    function update() {
        // queue the next update
        window.requestAnimationFrame(update);

        var date2 = new Date();
        var seconds2 = date2.getSeconds();

        // generate particle ever second
        if (seconds2 != seconds){
            y_generation_pos = 0
            if (initial_user_device == 0) {
                y_generation_pos = canvas.height*0.25;
                initial_user_device = 1
            }
            else if (initial_user_device == 1){
                y_generation_pos = canvas.height*0.5;
                initial_user_device = 2
            } else{
                y_generation_pos = canvas.height*0.75;
                initial_user_device = 0
            }
            packet = new Circle(position_user_devices + 25, y_generation_pos, packet_radius, packet_color)
            packet.velocitiesToPoint(position_queue_start, canvas.height*0.5, 5);
            pre_queue.push(packet);   
            seconds = seconds2;
        }

        // change packet velocity when start of queue is reached
        for (var i = 0; i < pre_queue.length; i++) {
            pre_queue[i].move();
            pre_queue[i].bound(position_queue_start);
        }

        // add packets to queue when queue is reached, and set velocity to 5 
        if (pre_queue.length > 0) {
            if (pre_queue[0].x_pos >= position_queue_start){
                packet = pre_queue.shift();
                packet.x_pos = position_queue_start
                packet.y_pos = canvas.height * 0.5
                packet.dx = 5
                packets.push(packet)
            }
        }


        // make particle queue up halfway on canvas
        initial_bound = 0
        for (var i = 0; i < packets.length; i++) {
            packets[i].move();
            if (i == 0){
                packets[i].bound(position_queue_end);
                initial_bound = position_queue_end
            }
            else{
                new_bound = initial_bound -packet_radius*3
                packets[i].bound(new_bound);
                initial_bound = new_bound
            }
        }

        // make packet wait at middle
        if (packets.length > 0){
            if (packets[0].x_pos >= position_queue_end){
                packets[0].sleep -= 1
            }

            // remove packet from queue and move queue forward
            if (packets[0].x_pos >= position_queue_end && packets[0].sleep < 0){
                consumed_packet = packets.shift();
                if (initial_server == 0){
                    consumed_packet.velocitiesToPoint(position_servers + 50, canvas.height*0.4, 5);
                    initial_server = 1
                } else{
                    consumed_packet.velocitiesToPoint(position_servers + 50, canvas.height*0.6, 5);
                    initial_server = 0
                }
                consumed_packets.push(consumed_packet);
                for (var i = 0; i < packets.length; i++) {
                    packets[i].dx = 5
                }
            }        
        }

        // update velocity of packet towards server
        for (var i = 0; i < consumed_packets.length; i++){
            consumed_packets[i].move();
            consumed_packets[i].bound(position_servers + 50);
        }

        // remove packets outside of screen
        survived = []
        for (var i = 0; i < consumed_packets.length; i++){
            if (consumed_packets[i].x_pos <= canvas.width - 100){
                survived.push(consumed_packets[i])
            }
        }
        consumed_packets = survived


        draw();

    }

    // start our code once the page has loaded
    document.addEventListener('DOMContentLoaded', init);
})()