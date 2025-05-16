import {
  flexRender,
  getCoreRowModel,
  GroupColumnDef,
  useReactTable,
  Column,
} from "@tanstack/react-table";
import { ColumnFiltersState,getFilteredRowModel } from "@tanstack/react-table";
import { useState, useEffect , useMemo } from 'react'

export type Show = {
  show: {
    status: string;
    name: string;
    type: string;
    language: string;
    genres: string[];
    runtime: number;
  };
};

// now create types for props for this Table component(https://tanstack.com/table/latest/docs/framework/react/examples/sub-components)
type TableProps<TData> = {
  data: TData[];
  columns: GroupColumnDef<TData>[];
};
export default function Table({ columns, data }: TableProps<Show>) {
  //use the useReact table Hook to build our table:
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    //pass in our data
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
getFilteredRowModel: getFilteredRowModel(), //row model to filter the table

    state: {
      columnFilters,
    },
    onColumnFiltersChange: setColumnFilters,
  });
  // Table component logic and UI come here
  return (
       <div>
      <table>
        <thead>
          {/*use the getHeaderGRoup function to render headers:*/}
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} colSpan={header.colSpan}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {/*Now render the cells*/}
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

//create a Filter component to use for column searching:
function Filter({ column }: { column: Column<Show, unknown> }) {
  const columnFilterValue = column.getFilterValue();

  return (
    <Searchbar
      onChange={(value) => {
        column.setFilterValue(value);
      }}
      placeholder={`Search...`}
      type="text"
      value={(columnFilterValue ?? "") as string}
    />
  );
}
//Create a searchbar:
function Searchbar({
  value: initialValue,
  onChange,
  ...props
}: {
  value: string | number;
  onChange: (value: string | number) => void;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange">) {
  const [value, setValue] = useState(initialValue);
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);
  //if the entered value changes, run the onChange handler once again.
  useEffect(() => {
    onChange(value);
  }, [value]);
  //render the basic searchbar:
  return (
    <input
      {...props}
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}