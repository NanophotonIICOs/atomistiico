using FileIO

current_dir = @__DIR__
function make_dir(dir_path::String = current_dir)
        if !isdir(dir_path)
            mkdir(dir_path)
        end
end