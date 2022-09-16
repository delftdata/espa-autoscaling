class Server {
    constructor(x, y, width, height, color, device_type, status) {
        this.x_pos = x;
        this.y_pos = y;
        this.width = width;
        this.height = height
        this.color = color
        this.device_type = device_type
        this.status = status;
        this.packet = -1;
        this.time = new Date().getTime();
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

    generatePacket(time2, offset, rate, size, speed){
        if (time2 - this.time > rate + 90*offset){
        var generated_packet = new Circle(this.x_pos + size / 2, this.y_pos + size / 2, size / 10, packet_color, speed);
        generated_packet.velocitiesToPoint(position_queue_start, canvas.height*0.5, speed);
        this.time = time2
        return generated_packet;
        }
        return null;
    }
}

class Circle {
    constructor(x, y, radius, color, speed) {
        this.x_pos = x;
        this.y_pos = y;
        this.radius = radius;
        this.dx = speed;
        this.dy = 0;
        this.color = color
        this.sleep = 200
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

class Button {
    constructor(x, y, width, height, text, type, increase) {
        this.x_pos = x;
        this.y_pos = y;
        this.width = width;
        this.height = height;
        this.text = text;
        this.type = type
        this.increase = increase;
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 5;
        ctx.fillStyle = 'white';
        ctx.fillRect(this.x_pos, this.y_pos, this.width, this.height);
        ctx.stroke();


    }

    drawText(ctx) {
        ctx.beginPath();
        ctx.font = String(this.width) +"px Arial";
        ctx.strokeStyle = 'white';
        ctx.fillStyle = 'white';
        ctx.fillText(this.text, this.x_pos - this.width*11, this.y_pos + this.width / 1.7);
        ctx.stroke()
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
        canvas.height = innerHeight / 2 ;

        og_date = new Date();
        date = new Date();
        seconds = date.getSeconds();
        time = date.getTime();
        
        position_user_devices = 0.05 * canvas.width

        position_servers = 0.95 * canvas.width

        position_queue_start = 0.2 * canvas.width

        position_queue_end = 0.8 * canvas.width
        
        cooldown = 0;

        object_heights = canvas.height / 10


        speed = object_heights / 5;
        packet_queue_distance = speed*2;


        rate = 1500

        packet_radius = 5;

        packet_color = 'red';


        pre_queue = [];

        packets = [];

        consumed_packets = [];

        min_servers = 2;
        max_servers = 4;

        servers = [];
        online_servers = 1;
        online_user_devices = 1;

        initial_server = 0;

        initial_user_device = 0;

        localStorage.setItem('queue_length', 0);
        localStorage.setItem('servers', 0);

        buttons = []

        button_xpos = 0.4 * canvas.width

        increase_button_ypos = 0.9 * canvas.height
        decrease_button_ypos = 0.8 * canvas.height
        rate_increase_button_ypos = 0.7 * canvas.height
        rate_decrease_button_ypos = 0.6 * canvas.height

        buttons.push(new Button(button_xpos, 0.6 * canvas.height, object_heights / 2, object_heights / 2, "Decrease user devices:", "user", false))
        buttons.push(new Button(button_xpos, 0.7 * canvas.height, object_heights / 2, object_heights / 2, "Increase user devices:", "user", true))
        buttons.push(new Button(button_xpos, 0.8 * canvas.height, object_heights / 2, object_heights / 2, "Decrease load:", "rate", false))
        buttons.push(new Button(button_xpos, 0.9 * canvas.height, object_heights / 2, object_heights / 2, "Increase load:", "rate", true))


        canvas.addEventListener('click', function(evt) {
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].x_pos
                buttons[i].y_pos
                buttons[i].width
                buttons[i].length
                if (evt.clientX > buttons[i].x_pos && evt.clientX < buttons[i].x_pos+buttons[i].width && evt.clientY < buttons[i].y_pos+buttons[i].height && evt.clientY > buttons[i].y_pos){
                    if (buttons[i].type === "rate" && buttons[i].increase && rate > 200){
                        rate -= 200;
                    } else if (buttons[i].type === "rate" && !buttons[i].increase){
                        rate += 200;
                    } else if (buttons[i].type === "user" && buttons[i].increase && online_user_devices < 3){
                        online_user_devices += 1;

                    } else if (buttons[i].type === "user" && !buttons[i].increase && online_user_devices > 1){
                        online_user_devices -= 1;
                    } else{
                    }
                }}}, false);
                

        // servers
        servers.push(new Server(position_servers, canvas.height*0.8 - object_heights, object_heights*2, object_heights*2, "blue", "server", "offline"))
        servers.push(new Server(position_servers, canvas.height*0.6 - object_heights, object_heights*2, object_heights*2, "blue", "server", "offline"))
        servers.push(new Server(position_servers, canvas.height*0.4 - object_heights, object_heights*2, object_heights*2, "blue", "server", "online"))
        servers.push(new Server(position_servers, canvas.height*0.2 - object_heights, object_heights*2, object_heights*2, "blue", "server", "offline"))

        // user devices
        servers.push(new Server(position_user_devices, canvas.height*0.75 - object_heights / 2, object_heights, object_heights, "green", "client", "offline"))
        servers.push(new Server(position_user_devices, canvas.height*0.5 - object_heights / 2, object_heights, object_heights, "green", "phone", "offline"))
        servers.push(new Server(position_user_devices, canvas.height*0.25 - object_heights / 2, object_heights, object_heights, "green", "client", "online"))

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

        // main line
        ctx.moveTo(position_queue_start, canvas.height / 2);
        ctx.lineTo(position_queue_end, canvas.height / 2);

        // draw user device lines
        for (var i = 0; i < servers.length; i++) {
            if (servers[i].device_type !== "server" && servers[i].status === "online"){
                ctx.moveTo(servers[i].x_pos + object_heights /2, servers[i].y_pos + object_heights / 2);
                ctx.lineTo(position_queue_start, canvas.height / 2);
            }
        }
        

        // draw server lines
        for (var i = 0; i < servers.length; i++) {
            if (servers[i].device_type === "server" && servers[i].status === "online"){
                ctx.moveTo(position_queue_end, canvas.height / 2);
                ctx.lineTo(position_servers + object_heights , servers[i].y_pos + object_heights);
            }
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // draw buttons
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].draw(ctx);
            buttons[i].drawText(ctx);
        }

        for (var i = 0; i < servers.length; i++) {
            if (servers[i].status === "online"){
                servers[i].draw(ctx);
            }
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
        var time2 = date2.getTime();

        for (var i = 0; i < servers.length; i++){
            if (servers[i].device_type !== "server" && servers[i].status === "online"){
                generated = servers[i].generatePacket(time2, i, rate, object_heights, speed);
                if (generated !== null){
                    pre_queue.push(generated);
                }
            }    
        }

        // generate particle ever second
        if (seconds2 != seconds){  
            seconds = seconds2;
            cooldown -= 1;
            localStorage.setItem('queue_length', packets.length);
            localStorage.setItem('servers', online_servers);
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
                packet.dx = speed;
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
                new_bound = initial_bound - packet_queue_distance;
                packets[i].bound(new_bound);
                initial_bound = new_bound
            }
        }

        // find server with no packet assigned
        initial_server = -1;
        for (var i = 0; i < servers.length; i++) {
            if (servers[i].device_type === "server" && servers[i].status === "online" && servers[i].packet == -1){
                initial_server = i;
            }
        }

        // make packet wait at middle
        if (packets.length > 0){
            if (packets[0].x_pos >= position_queue_end){
                packets[0].sleep -= 1
            }

            // remove packet from queue and move queue forward
            if (packets[0].x_pos >= position_queue_end && initial_server >= 0){
                consumed_packet = packets.shift();
                consumed_packet.velocitiesToPoint(position_servers + object_heights, servers[initial_server].y_pos + object_heights, speed);
                // consumed_packet.velocitiesToPoint(position_servers + 50, servers[initial_server].y_pos + 50, speed);
                servers[initial_server].packet = consumed_packet
                consumed_packets.push(consumed_packet);
                for (var i = 0; i < packets.length; i++) {
                    packets[i].dx = speed;
                }
            }        
        }

        // update velocity of packet towards server
        for (var i = 0; i < consumed_packets.length; i++){
            consumed_packets[i].move();
            consumed_packets[i].bound(position_servers + object_heights);
        }

        // let server process packets
        for (var i = 0; i < servers.length; i++){
            if (servers[i].device_type === "server" && servers[i].packet != -1){
                servers[i].packet.sleep -= 1
                if (servers[i].packet.sleep <= 0){
                    servers[i].packet = -1;
                }
            }
        }

        // add servers if queue length is more than 10
        if (packets.length > 15 && online_servers <= max_servers && cooldown <= 0){
            for (var i = 0; i < servers.length; i++){
                if (servers[i].status === "offline" && servers[i].device_type === "server"){
                    servers[i].status = "online";
                    online_servers += 1;
                    cooldown = 10
                    break;
                }
            }
        }

        // remove servers if queue length is less than 5
        if (packets.length < 5 && online_servers > min_servers && cooldown <= 0){
            for (var i = 0; i < servers.length; i++){
                if (servers[i].status === "online" && servers[i].device_type === "server"){
                    servers[i].status = "offline";
                    servers[i].packet.sleep = 0;
                    online_servers -= 1;
                    cooldown = 10
                    break;
                }
            }
        }

        // remove packets after they have finished processing
        survived = []
        for (var i = 0; i < consumed_packets.length; i++){
            if (consumed_packets[i].sleep > 0){
                survived.push(consumed_packets[i])
            }
        }
        consumed_packets = survived

        // count number of user devices online
        current_number_online_users = 0     
        for (var i = 0; i < servers.length; i++){
            if (servers[i].status === "online" && servers[i].device_type != "server"){
                current_number_online_users+= 1
            }
        }

        // turn user device on 
        for (var i = 0; i < servers.length; i++){
            if (servers[i].status === "offline" && servers[i].device_type !== "server" && current_number_online_users < online_user_devices){
                servers[i].status = "online";
                break;
            }
        }

        // turn user device off
        for (var i = 0; i < servers.length; i++){
            if (servers[i].status === "online" && servers[i].device_type !== "server" && current_number_online_users > online_user_devices){
                servers[i].status = "offline";
                break;
            }
        }
        

        // // adjust rate at which packets are prodcued
        // if (rate_change_cooldown <= 0){
        //     if (rate_index < 4){
        //         rate_index += 1;
        //     } else{
        //         rate_index = 0;
        //     }
        //     rate = rates[rate_index];
        //     rate_change_cooldown = 60;
        //     console.log("changing rate to");
        //     console.log(rate);
        // }

        draw();

    }

    // function getMousePos(canvas, event) {
    //     var rect = canvas.getBoundingClientRect();
    //     return {
    //         x: event.clientX - rect.left,
    //         y: event.clientY - rect.top
    //     };
    // }
    // //Function to check whether a point is inside a rectangle
    // function isInside(pos, rect){
    //     return pos.x > rect.x && pos.x < rect.x+rect.width && pos.y < rect.y+rect.height && pos.y > rect.y
    // }

    // //The rectangle should have x,y,width,height properties
    // var rect = {
    //     x:250,
    //     y:350,
    //     width:200,
    //     height:100
    // };
    // //Binding the click event on the canvas
    // canvas.addEventListener('click', function(evt) {
    //     console.log('hello')
    // }

    // canvas.addEventListener('click', function(evt) {
    //     console.log("hello")
    //     var mousePos = getMousePos(canvas, evt);
    
    //     if (isInside(mousePos,rect)) {
    //         alert('clicked inside rect');
    //     }else{
    //         alert('clicked outside rect');
    //     }   
    // }, false);

    // start our code once the page has loaded
    document.addEventListener('DOMContentLoaded', init);
})()