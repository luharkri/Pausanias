fn main() {
    loop{
        println!("input 1 = ");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input).unwrap();
        let _input = input.trim();       
        let left: f64 = _input.parse().unwrap();
        

        println!("input 2 = ");
        let mut input2 = String::new();
        std::io::stdin().read_line(&mut input2).unwrap();
        let _input2 = input2.trim();       
        let left2: f64 = _input2.parse().unwrap();

        let _final_val = left + left2 ;
        println!("final val = ");
        println!("{}", _final_val);
    }
    
}
