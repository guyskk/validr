## walkdict 

walkdict is a tool to deep traversal dict and list, no Recursion Depth limit

walkdict可以用来深度遍历dict和list，不受dict嵌套深度限制

##install 安装

	pip install walkdict

## usage 用法

```python
>>> from walkdict import walkdict
>>> d={"key":"value","inner":{"inner-key":"inner-value","list":[1,2,3,4]}}
>>> for k,v in walkdict(d):
... 	print k,v
... 
key value
inner.inner-key inner-value
inner.list.[0] 1
inner.list.[1] 2
inner.list.[2] 3
inner.list.[3] 4
```

when dict's key is a class, the key name will be $classname 

当dict的key是一个类时，将会显示$classname 

```python
>>> from datetime import datetime
>>> from walkdict import walkdict
>>> d={datetime:"value","time":datetime}
>>> for k,v in walkdict(d):
... 	print k,v
... 
$datetime value
time <type 'datetime.datetime'>
```


## note 注意事项

can't process circulation dict or list which will cause program frozen

无法处理循环引用的dict和list，将会导致程序假死，一直运行而无法正常退出

for example 例如

```python
>>> from walkdict import walkdict
>>> d={"key":"value"}
>>> d["key"]=d
>>> for k,v in walkdict(d):
... 	print k,v
```

## test 测试
	
	py.test

## license 

MIT License